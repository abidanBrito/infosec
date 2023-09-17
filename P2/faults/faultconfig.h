#ifndef _FAULTABLE_H_
#define _FAULTABLE_H_

#define FAULTCONFIG_CONCATENATE_DETAIL(x, y) x##y
#define FAULTCONFIG_CONCATENATE(x, y) FAULTCONFIG_CONCATENATE_DETAIL(x, y)
#define FAULTCONFIG_MAKE_UNIQUE(x) FAULTCONFIG_CONCATENATE(x, __COUNTER__)

#define FAULT_CONFIG_HEADER asm volatile(".asciz \"FAULTCONFIG\"");

#define FAULT_CONFIG_DETAIL(fnc, x) void fnc(void) { FAULT_CONFIG_HEADER asm volatile(".asciz " #x ); };
#define FAULT_CONFIG(x) FAULT_CONFIG_DETAIL(FAULTCONFIG_MAKE_UNIQUE(__fc_magic_), x)

#define FAULT_CONFIG_DETAIL_A(fnc, x, y) void fnc(void) { FAULT_CONFIG_HEADER asm volatile(".asciz " #x "\n.dc.a " #y); };
#define FAULT_CONFIG_A(x, y) FAULT_CONFIG_DETAIL_A(FAULTCONFIG_MAKE_UNIQUE(__fc_magic_), x, y)

#endif
