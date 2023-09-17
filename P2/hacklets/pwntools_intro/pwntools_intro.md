# Pwntools intro
When it comes to writing exploits, [Pwntools](https://docs.pwntools.com/en/stable/#) is extremely useful. Pwntools can be installed by following [instructions](https://docs.pwntools.com/en/stable/install.html#command-line-tools). The Pwntools documentation itself is also good and includes a [how to get started](https://docs.pwntools.com/en/stable/intro.html) page. We will cover the basics that should get you started quickly and help you solve the hacklets.

The three main topics we will discuss in this introduction are:

1. Send input to binary and receive output
2. Input formatting
3. pwngdb 

## 1. Send input to binary and receive output
Solving hacklets requires writing exploits that run **locally** on the binary. You can use pwntools to make remote connections, but we will focus on local exploitation.

To **start a binary** all you need to do is call the function:

```python
from pwn import *

p = process(<path_to_binary>)
```

The process command will spawn a new process (in our case start the binary) and setup a tube for communication. 

In order to **send data** to the process we can use the `sendline()` function:

```python
p.sendline(b'Hello')
```

When using [sendline](https://docs.pwntools.com/en/stable/tubes.html?highlight=sendline#pwnlib.tubes.tube.tube.sendline) keep in mind that pwntools automatically appends a newline to the data you are sending. If you don't want this behavior you can use [send(data)](https://docs.pwntools.com/en/stable/tubes.html?highlight=sendline#pwnlib.tubes.tube.tube.send) instead. 

In order to receive data there are a multitude of functions you can use. The 3 most commonly used once are:

### 1. recvline()
[doc](https://docs.pwntools.com/en/stable/tubes.html?highlight=sendline#pwnlib.tubes.tube.tube.recvline) 

Receive a single line which is defined as (\<data\> + \<newline\>)

Example:

```c
int main()
{
	printf("Hello\n");
	printf("World\n");
	return 0;
}
```

```python
p.recvline()
'Hello'
```
###  2. recvuntil(search_string)
[doc](https://docs.pwntools.com/en/stable/tubes.html?highlight=sendline#pwnlib.tubes.tube.tube.recvuntil) 

Receive data until the the provided search_string is encountered

```c
int main()
{
	printf("Hello\n");
	printf("World\n");
	return 0;
}
```

```python
p.recvuntil('l')
'Hel'
```

###  3. recv()
[doc](https://docs.pwntools.com/en/stable/tubes.html?highlight=sendline#pwnlib.tubes.tube.tube.recv)

As soon as any data is available inside the tube `recv` immediately returns it. It only will return 4096 bytes if not specified otherwise. 

```c
int main()
{
	printf("Hello World\n");
	return 0;
}
```

```python
p.recv()
'Hello World'
```

For testing out a program `recv()` is fine but if you want your exploit to be as reliable and predictable as possible you should use `recvuntil` or `recvline`.

It is not necessary to receive the output of the program first, and then send data to it once you have received everything. Nonetheless, it is recommended that you try because otherwise unintended behaviors can arise. Best practice is to:

Best practice is to:

1. Get all output of a program (using `recvuntil`, etc)
2. Send input to program (using `sendline` or `send`)
3. Go back to step 1

## Input formatting

During the exercise, you will have to provide address as an input to a binary. While Python can sometimes be a bit finicky when it comes to converting between different datatypes and formats, it is one of the most viable options.

For converting addresses to input it is important to keep in mind the endianness of a system (namely, small and big endian). Depending on the endianness of a system, you might have to reorder your address input.

The most useful group of functions to achieve the reordering and to convert a hex number into bytes (which you need in order to use it as an input) is the pwntools packing functions [doc](https://docs.pwntools.com/en/stable/util/packing.html). 

Here is a simple example who to convert a hex address into bytes which can be used by `sendline()` and reordes the bytes since it is little endian for a 32 bit integer.

```python
p32(0xdeadbeef, endian='little')
b'\xef\xbe\xad\xde'
```
This simple packing function is already quite useful, put pwntools has a lot more to offer in terms of packing and unpacking integers and strings. Once again the [documentation](https://docs.pwntools.com/en/stable/util/packing.html) is great and provides you with more examples and details.


## pwndbg 

You will have to use some form of debugging to solve the challenges and while gdb can look intimidating but [pwndbg](https://github.com/pwndbg/pwndbg) helps out a lot when trying to debug a binary. 

In this tutorial we will not go into great detail on how to use gdb. We will just quickly cover the 4 most important commands that should help you to get started:

- `run` runs the program
- `break <where>` set a breakpoint. Example: `break main`
- `next` Go to the next instruction and do not go into function (source code)
- `step` Go to the next instruction and go into function (assembly code)
- `continue` Continue with normal execution
- `x/<n>x *<address>` / `x/<n>x <var_name>` prints out `n` bytes of memory at the address or the address of a variable

You can use the **short version** of each command by just typing the first letter of the command (Example: `break main` -> `b main`, `continue` -> `c`)

For more details on how to use gdb have a look at this [cheat sheet](https://darkdust.net/files/GDB%20Cheat%20Sheet.pdf).



We will explain each section of the pwngdb interface to give you a better understanding of what information pwngdb provides you

![Alt text](img/pwngdb.png?raw=true "pwndbg")

In total we have 5 sections and we will quickly go over each off them. 

### 1. Register
Shows you the value of each register. pwndbg also shows you the content of memory locations and decodes them into strings.
### 2. DISASM
The DISASM sections shows you the assembly code. It shows the current instruction hightlighted in green and some of the subsequent instructions. 
### 3. Source Code
If the binary you are analyizing containes debugging information you will see the orignal source code which makes it easly readable. 
### 4. Stack
The Stack sections displays part of the current stack and some values that are stored on it. (**Pro Tip**: If you want to see more of the stack you can input `stack 40` which will display 40 entries of the current stack)
### 5. Backtrace
Backtrace shows you what functions where called so fare. It does so by checking the return addresses that are on the stack (Quite usefull if you want to find out what the return address is)


## Additional information & usefull command line tools

One extremely useful command is `pwn template` [doc](https://docs.pwntools.com/en/stable/commandline.html#pwn-template).
Example: `pwn template ./main`
This command generates a full exploit framework and reduces the amount of time you need to spent to set everything up. 
If you store the output of  `pwn template` into a file like `exploit.py` you can start interacting the binary you want to exploit and add your payloads. 
You can start your program with `./exploit GDB` which will launch gdb and you can provided your gdb script, which makes debugging faster. 

- [pwntools-doc](https://docs.pwntools.com/en/stable/index.html)
- [pwntools-cheatsheet](https://gist.github.com/anvbis/64907e4f90974c4bdd930baeb705dedf)

