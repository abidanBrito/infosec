#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/ptrace.h>
#include <errno.h>
#include <sys/user.h>
#include <stdint.h>
#include <stdarg.h>
#include <time.h>
#include <sys/personality.h>
#include <elf.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <inttypes.h>

#include "simulator.h"

// ------------------------------------------------------------------------------------------------
static Config config = {
    .skip_min = -15,
    .skip_max = 15,
    .timeout = 30,
    .aslr = 1,
    .exitmsg = 1
};

static Command* commands = NULL;
static int commands_count = 0;
static int commands_len = 0;
static const char* command_name[__FAULT_END__];

static size_t instruction_counter = 0;
static size_t fault_cooldown = 0;
static size_t allowed_faults = SIZE_MAX;

static size_t start_time;

static size_t textstart;
static size_t textend;


// ------------------------------------------------------------------------------------------------
void tagged_printf(const char* tag, const char * format, ...) {
  va_list args;
  fprintf(stderr, "%s", tag);
  va_start(args, format);
  vfprintf(stderr, format, args);
  va_end(args);
}


// ------------------------------------------------------------------------------------------------
int add_command(Command* c, size_t line_nr) {
    if(config.fault_blacklist & c->type) {
        ERROR(TAG_LINE "Command '%s' not allowed for this binary!\n", line_nr, command_name[c->type]);
        return 1;
    }
    if(commands == NULL) {
        commands_len = 128;
        commands = (Command*)malloc(commands_len * sizeof(Command));
    }
    commands[commands_count++] = *c;
    if(commands_count == commands_len) {
        commands_len *= 2;
        commands = (Command*)realloc(commands, commands_len * sizeof(Command));
    }
    return 0;
}


// ------------------------------------------------------------------------------------------------
int parse_position(char* pos, Command* c, size_t line_nr) {
    if(!pos || strlen(pos) == 0) {
        ERROR(TAG_LINE "No position given\n", line_nr);
        return 1;
    }
    if(pos[0] == '@') {
        // absolute RIP
        if(config.position_blacklist & RIP) {
            ERROR(TAG_LINE "RIP-based faulting not allowed for this binary!\n", line_nr);
            return 1;
        }
        c->rip = strtoull(pos + 1, NULL, 0);
        c->position = RIP;
    } else if(pos[0] == '#') {
        // instruction count
        if(config.position_blacklist & INSTRUCTION) {
            ERROR(TAG_LINE "Instruction-count-based faulting not allowed for this binary!\n", line_nr);
            return 1;
        }
        c->instruction = strtoull(pos + 1, NULL, 0);
        c->position = INSTRUCTION;
    } else {
        ERROR(TAG_LINE "Unsupported position '%s'\n", line_nr, pos);
        return 1;
    }
    return 0;
}

// ------------------------------------------------------------------------------------------------
int parse_command(char* cmd, size_t line_nr) {
    char* command = strtok(cmd, DELIMITER);
    Command c;

    if(!command) return 0;
    if(strlen(command) == 0) return 0;
    if(command[0] == '#') return 0; // comment

    if(!strcasecmp(command, command_name[SKIP])) {
        c.type = SKIP;
        c.index = atoi(strtok(NULL, DELIMITER));
        if((ssize_t)c.index < (ssize_t)config.skip_min) {
            ERROR(TAG_LINE "Skip must be >= %d\n", line_nr, config.skip_min);
            return 1;
        }
        if(c.index > config.skip_max) {
            ERROR(TAG_LINE "Skip must be <= %d\n", line_nr, config.skip_max);
            return 1;
        }
        if(parse_position(strtok(NULL, DELIMITER), &c, line_nr)) {
            return 1;
        }
    } else if(!strcasecmp(command, command_name[LOG])) {
        c.type = LOG;
        char* type = strtok(NULL, DELIMITER);
        if(!strcasecmp(type, "inscnt")) {
            c.log = LOG_INSTRUCTION;
        } else if(!strcasecmp(type, "rip")) {
            c.log = LOG_RIP;
        } else if(!strcasecmp(type, "fault")) {
            c.log = LOG_FAULT;
        } else {
            ERROR(TAG_LINE "Unknown logging target '%s'\n", line_nr, type);
            return 1;
        }
        if(c.log & config.log_blacklist) {
            ERROR(TAG_LINE "Logging type '%s' not allowed for this binary!\n", line_nr, type);
            return 1;
        }
    } else if(!strcasecmp(command, command_name[HAVOC])) {
        c.type = HAVOC;
        c.destination = strtoull(strtok(NULL, DELIMITER), NULL, 0);
        if(parse_position(strtok(NULL, DELIMITER), &c, line_nr)) {
            return 1;
        }
    } else if(!strcasecmp(command, command_name[ZERO])) {
        c.type = ZERO;
        c.destination = strtoull(strtok(NULL, DELIMITER), NULL, 0);
        if(parse_position(strtok(NULL, DELIMITER), &c, line_nr)) {
            return 1;
        }
    } else if(!strcasecmp(command, command_name[BITFLIP])) {
        c.type = BITFLIP;
        c.index = atoi(strtok(NULL, DELIMITER));
        c.destination = strtoull(strtok(NULL, DELIMITER), NULL, 0);
        if(parse_position(strtok(NULL, DELIMITER), &c, line_nr)) {
            return 1;
        }
    } else {
        return 1;
    }
    
    if(c.type & (BITFLIP | HAVOC | ZERO)){
        if(c.destination >= textstart && c.destination < textend){
            ERROR(TAG_LINE "Memory corruption in .text section not allowed!\n", line_nr);
            return 1;
        }
    }
    
    if(add_command(&c, line_nr)) return 1;
    return 0;
}

// ------------------------------------------------------------------------------------------------
int parse_script(char* file) {
    command_name[SKIP] = "skip";
    command_name[LOG] = "log";
    command_name[BITFLIP] = "bitflip";
    command_name[HAVOC] = "havoc";
    command_name[ZERO] = "zero";

    DEBUG("Parsing %s...\n", file);
    FILE* f = fopen(file, "r");
    if(!f) {
        ERROR("Could not open script file '%s'\n", file);
        return 1;
    }
    char* line = NULL;
    size_t len = 0;
    size_t line_nr = 0;
    while(getline(&line, &len, f) != -1) {
        if(parse_command(line, ++line_nr)) {
            ERROR(TAG_LINE "Could not parse command '%s'\n", line_nr, line);
            return 1;
        }
        free(line);
        line = NULL;
        len = 0;
    }

    fclose(f);
    return 0;
}

// ------------------------------------------------------------------------------------------------
void parse_config(char* binary) {
    FILE *f = fopen(binary, "rb");
    if(!f) return;
    fseek(f, 0, SEEK_END);
    size_t fsize = ftell(f);
    fseek(f, 0, SEEK_SET);
    char* elf = (char*)malloc(fsize);
    if(!elf) {
        fclose(f);
        return;
    }
    fread(elf, fsize, 1, f);
    for(size_t i = 0; i < fsize - 24; i++) {
        if(!strcmp(elf + i, "FAULTCONFIG")) {
            char* conf = elf + i + 12;
            if(!strcmp(conf, "NOZERO")) config.fault_blacklist |= ZERO;
            if(!strcmp(conf, "NOHAVOC")) config.fault_blacklist |= HAVOC;
            if(!strcmp(conf, "NOSKIP")) config.fault_blacklist |= SKIP;
            if(!strcmp(conf, "NOBITFLIP")) config.fault_blacklist |= BITFLIP;
            if(!strcmp(conf, "NOLOG")) config.fault_blacklist |= LOG;
            if(!strcmp(conf, "NOASLR")) config.aslr = 0;
            if(!strcmp(conf, "NOEXITMSG")) config.exitmsg = 0;
            if(!strcmp(conf, "NOLOGFAULT")) config.log_blacklist |= LOG_FAULT;
            if(!strcmp(conf, "NOLOGRIP")) config.log_blacklist |= LOG_RIP;
            if(!strcmp(conf, "NOLOGINSTRUCTION")) config.log_blacklist |= LOG_INSTRUCTION;
            if(!strcmp(conf, "NORIPTRIGGER")) config.position_blacklist |= RIP;
            if(!strcmp(conf, "NOINSTRUCTIONTRIGGER")) config.position_blacklist |= INSTRUCTION;
            if(!strncmp(conf, "MINSKIP=", 8)) config.skip_min = atoi(conf + 8);
            if(!strncmp(conf, "MAXSKIP=", 8)) config.skip_max = atoi(conf + 8);
            if(!strncmp(conf, "TIMEOUT=", 8)) config.timeout = atoi(conf + 8);
            if(!strncmp(conf, "FAILEVERY=", 10)) config.fail_every = atoi(conf + 10);
            if(!strncmp(conf, "SEED=", 5)) config.seed = atoi(conf + 5);
            if(!strncmp(conf, "COOLDOWN=", 9)) config.cooldown = strtoull(conf + 9, NULL, 0);
            if(!strncmp(conf, "MAXFAULTS=", 10)) config.max_faults = strtoull(conf + 10, NULL, 0);

            if(!strcmp(conf, "MAIN")) {
                config.main = *(void **)(conf + 5);
                DEBUG("Main: %p\n", config.main);
            }

            DEBUG("Config: %s\n", conf);
        }
    }
    free(elf);
    fclose(f);
}
// ------------------------------------------------------------------------------------------------
//via: https://stackoverflow.com/questions/18418839/how-can-i-get-the-offset-and-size-of-the-text-section-of-a-binary
void find_section(char* binary, char* section, size_t* start, size_t* end){
    int fd = open(binary, O_RDONLY);

    /* map ELF file into memory for easier manipulation */
    struct stat statbuf;
    fstat(fd, &statbuf);
    char *fbase = mmap(NULL, statbuf.st_size, PROT_READ, MAP_SHARED, fd, 0);

    Elf64_Ehdr *ehdr = (Elf64_Ehdr *)fbase;
    Elf64_Shdr *sects = (Elf64_Shdr *)(fbase + ehdr->e_shoff);
    int shsize = ehdr->e_shentsize;
    int shnum = ehdr->e_shnum;
    int shstrndx = ehdr->e_shstrndx;

    /* get string table index */
    Elf64_Shdr *shstrsect = &sects[shstrndx];
    char *shstrtab = fbase + shstrsect->sh_offset;

    int i;
    for(i=0; i<shnum; i++) {
        if(!strcmp(shstrtab+sects[i].sh_name, section)) {
            *start = sects[i].sh_addr;
            *end = sects[i].sh_addr + sects[i].sh_size;
        }
    }
    
    close(fd);
    return;
}


// ------------------------------------------------------------------------------------------------
void show_status(int status) {
    if(WIFSTOPPED(status)) {
        DEBUG("Child stopped: %d\n", WSTOPSIG(status));
    }
    if(WIFEXITED(status)) {
        DEBUG("Child exited: %d\n", WEXITSTATUS(status));
    }
    if(WIFSIGNALED(status)) {
        DEBUG("Child signaled: %d\n", WTERMSIG(status));
    }
    if(WCOREDUMP(status)) {
        DEBUG("Core dumped.\n");
    }
}

// ------------------------------------------------------------------------------------------------
int ptrace_instruction_pointer(int pid) {
    struct user_regs_struct regs;
    if(ptrace(PTRACE_GETREGS, pid, NULL, (void*)&regs)) {
        fprintf(stderr, "Error fetching registers from child process: %s\n",
            strerror(errno));
        return 1;
    }

    int i, log_fault = 0;
    for(i = 0; i < commands_count; i++) {
        if(commands[i].type == LOG) {
            if(commands[i].log == LOG_RIP) {
                printf("RIP: 0x%zx\n", (size_t)regs.rip);
            } else if(commands[i].log == LOG_INSTRUCTION) {
                printf("Instruction #%zd\n", instruction_counter);
            } else if(commands[i].log == LOG_FAULT) {
                log_fault = 1;
            }
        }
    }

    if(fault_cooldown) fault_cooldown--;

    for(i = 0; i < commands_count; i++) {
        // Log commands are already handled above
        if (commands[i].type == LOG)
            continue;

        if((commands[i].position == RIP && commands[i].rip == regs.rip)
            || (commands[i].position == INSTRUCTION && instruction_counter == commands[i].instruction)) {

            if(allowed_faults == 0) {
                DEBUG("No more faults - skipping fault '%s'\n", command_name[commands[i].type]);
                if(log_fault) printf("Cannot induce fault '%s' - maximum amount of %d reached\n",
                                     command_name[commands[i].type], config.max_faults);
                continue;
            }

            if (allowed_faults != SIZE_MAX)
                allowed_faults--;

            if(fault_cooldown) {
                DEBUG("Cooldown - skipping fault '%s'\n", command_name[commands[i].type]);
                if(log_fault) printf("Cannot induce fault '%s' - last fault was too recent\n", command_name[commands[i].type]);
                continue;
            }

            fault_cooldown = config.cooldown;

            if(config.fail_every > 0) {
                if((rand() % config.fail_every) == 0) {
                    DEBUG("Command '%s' randomly failed\n", command_name[commands[i].type]);
                    continue;
                }
            }

            if(commands[i].type == SKIP) {
                DEBUG("Skip %d @ 0x%zx\n", commands[i].index, regs.rip);
                if(log_fault) printf("SKIP %d (RIP: 0x%zx, Instruction #%zd)\n", (int)commands[i].index, (size_t)regs.rip, instruction_counter);
                regs.rip += commands[i].index;
                ptrace(PTRACE_SETREGS, pid, NULL, &regs);
            } else if(commands[i].type == HAVOC) {
                DEBUG("Havoc 0x%zx @ 0x%zx\n", commands[i].destination, regs.rip);
                size_t val = rand();
                if(log_fault) printf("HAVOC 0x%zx -> %zd (RIP: 0x%zx, Instruction #%zd)\n", commands[i].destination, val, (size_t)regs.rip, instruction_counter);
                ptrace(PTRACE_POKEDATA, pid, commands[i].destination, val);
            } else if(commands[i].type == ZERO) {
                DEBUG("Zero 0x%zx @ 0x%zx\n", commands[i].destination, regs.rip);
                if(log_fault) printf("ZERO 0x%zx (RIP: 0x%zx, Instruction #%zd)\n", commands[i].destination, (size_t)regs.rip, instruction_counter);
                ptrace(PTRACE_POKEDATA, pid, commands[i].destination, 0);
            } else if(commands[i].type == BITFLIP) {
                DEBUG("Bitflip #%d -> 0x%zx @ 0x%zx\n", commands[i].index, commands[i].destination, regs.rip);
                if(log_fault) printf("BITFLIP #%d -> 0x%zx (RIP: 0x%zx, Instruction #%zd)\n", (int)commands[i].index, commands[i].destination, (size_t)regs.rip, instruction_counter);
                long val = ptrace(PTRACE_PEEKDATA, pid, commands[i].destination, 0);
                val ^= 1ull << commands[i].index;
                ptrace(PTRACE_POKEDATA, pid, commands[i].destination, val);
            }

        }
    }

    instruction_counter++;

    if(time(NULL) - start_time > config.timeout) {
        ERROR("Timeout of %zd seconds reached\n", config.timeout);
        return 1;
    }

    return 0;
}

// ------------------------------------------------------------------------------------------------
int singlestep(int pid) {
    int retval, status;
    retval = ptrace(PTRACE_SINGLESTEP, pid, 0, 0);
    if(retval) {
        return retval;
    }
    waitpid(pid, &status, 0);
    return status;
}

int wait_for_main(int pid) {
    long orig = ptrace(PTRACE_PEEKTEXT, pid, config.main, 0L);
    ptrace(PTRACE_POKETEXT, pid, config.main, (orig & 0xFFFFFFFFFFFFFF00L) | 0xCC);
    ptrace(PTRACE_CONT, pid, 0L, 0L);

    // Ugly, but no easy way to do this without busy waiting
    int status;
    int ret;
    do {
        ret = waitpid(pid, &status, WNOHANG);
        usleep(10000);
    } while (ret == 0 && time(NULL) - start_time < config.timeout);

    if(ret > 0 && WIFSTOPPED(status)) {
        ptrace(PTRACE_POKETEXT, pid, config.main, orig);

        struct user_regs_struct regs;
        if(ptrace(PTRACE_GETREGS, pid, NULL, (void*)&regs)) {
            perror("Error fetching registers from child process");
            return 0;
        }

        regs.rip -= 1;
        DEBUG("In function, patching back. RIP new: %p\n", regs.rip);

        ptrace(PTRACE_SETREGS, pid, NULL, &regs);
    }

    return status;
}

#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)

// ------------------------------------------------------------------------------------------------
int main(int argc, char ** argv, char **envp) {
    pid_t pid;
    int status;
    char *program, *script;
    int args_offset;
    
#if defined (FBINARY) && defined (FSCRIPT)
    program = TOSTRING(FBINARY);
    script = TOSTRING(FSCRIPT);
    args_offset = 0;
#else
    program = argv[2];
    script = argv[1];
    args_offset = 2;
    
    if (argc < 3) {
        ERROR("Usage: %s <fault script> <binary> [<arg0> <arg1> ...]\n", argv[0]);
        exit(-1);
    }
#endif

    find_section(program, ".text", &textstart, &textend);

    config.seed = time(NULL);
    parse_config(program);

    if(parse_script(script)) {
        exit(-1);
    }
    DEBUG("Loaded %d commands\n", commands_count);
    char ** child_args = (char**) &argv[args_offset];

    srand(config.seed);

    pid = fork();
    if(pid == -1) {
        ERROR("Error forking: %s\n", strerror(errno));
        exit(-1);
    }
    if(pid == 0) {
        // victim application
        if(ptrace(PTRACE_TRACEME, 0, 0, 0)) {
            ERROR("Error starting tracer: %s\n", strerror(errno));
            exit(-1);
        }
        if(!config.aslr) {
            // disable aslr
            personality(ADDR_NO_RANDOMIZE);
        }
        execve(program, child_args, envp);
    } else {
        // fault simulator
        waitpid(pid, &status, 0);
        show_status(status);

        if (config.max_faults > 0)
            allowed_faults = config.max_faults;

        start_time = time(NULL);

        // Wait for main if we have one
        if(WIFSTOPPED(status) && config.main) {
            status = wait_for_main(pid);
        }

        while(WIFSTOPPED(status)) {
            if(ptrace_instruction_pointer(pid)) {
                break;
            }
            status = singlestep(pid);
        }
        show_status(status);
        DEBUG("Detaching\n");
        ptrace(PTRACE_DETACH, pid, 0, 0);

        if(config.exitmsg){
            if(WIFEXITED(status) && WEXITSTATUS(status) == 0) {
                printf("\n\033[92mSuccessfully exploited %s!\033[0m\n", program);
            } else {
                printf("\n\033[91mFailed to exploit %s!\033[0m\n", program);
            }
        }
    }

    return 0;
}
