; ModuleID = "nova_module"
target triple = "x86_64-pc-windows-msvc"
target datalayout = ""

define void @"main"()
{
entry:
  %"a" = alloca i32
  store i32 5, i32* %"a"
  %"b" = alloca i32
  store i32 10, i32* %"b"
  %"load_a" = load i32, i32* %"a"
  %"load_b" = load i32, i32* %"b"
  %"sumtmp" = add i32 %"load_a", %"load_b"
  %".4" = bitcast [4 x i8]* @"fmt_1" to i8*
  %".5" = call i32 (i8*, ...) @"printf"(i8* %".4", i32 %"sumtmp")
  %"load_a.1" = load i32, i32* %"a"
  %"load_b.1" = load i32, i32* %"b"
  %"multmp" = mul i32 %"load_a.1", %"load_b.1"
  %".6" = bitcast [4 x i8]* @"fmt_2" to i8*
  %".7" = call i32 (i8*, ...) @"printf"(i8* %".6", i32 %"multmp")
  %"load_b.2" = load i32, i32* %"b"
  %"load_a.2" = load i32, i32* %"a"
  %"subtmp" = sub i32 %"load_b.2", %"load_a.2"
  %".8" = bitcast [4 x i8]* @"fmt_3" to i8*
  %".9" = call i32 (i8*, ...) @"printf"(i8* %".8", i32 %"subtmp")
  %"load_b.3" = load i32, i32* %"b"
  %"load_a.3" = load i32, i32* %"a"
  %"divtmp" = sdiv i32 %"load_b.3", %"load_a.3"
  %".10" = bitcast [4 x i8]* @"fmt_4" to i8*
  %".11" = call i32 (i8*, ...) @"printf"(i8* %".10", i32 %"divtmp")
  %"load_b.4" = load i32, i32* %"b"
  %"modtmp" = srem i32 %"load_b.4", 3
  %".12" = bitcast [4 x i8]* @"fmt_5" to i8*
  %".13" = call i32 (i8*, ...) @"printf"(i8* %".12", i32 %"modtmp")
  %"x" = alloca float
  store float 0x40091eb860000000, float* %"x"
  %"load_x" = load float, float* %"x"
  %"dbl" = fpext float %"load_x" to double
  %".15" = bitcast [4 x i8]* @"fmt_6" to i8*
  %".16" = call i32 (i8*, ...) @"printf"(i8* %".15", double %"dbl")
  %"negtmp" = sub i32 0, 7
  %"neg" = alloca i32
  store i32 %"negtmp", i32* %"neg"
  %"load_neg" = load i32, i32* %"neg"
  %".18" = bitcast [4 x i8]* @"fmt_7" to i8*
  %".19" = call i32 (i8*, ...) @"printf"(i8* %".18", i32 %"load_neg")
  %".20" = bitcast [17 x i8]* @"str_1" to i8*
  %".21" = bitcast [4 x i8]* @"fmt_8" to i8*
  %".22" = call i32 (i8*, ...) @"printf"(i8* %".21", i8* %".20")
  %"flag" = alloca i1
  store i1 1, i1* %"flag"
  %"load_flag" = load i1, i1* %"flag"
  %".24" = bitcast [5 x i8]* @"str_2" to i8*
  %".25" = bitcast [6 x i8]* @"str_3" to i8*
  %"boolstr" = select  i1 %"load_flag", i8* %".24", i8* %".25"
  %".26" = bitcast [4 x i8]* @"fmt_9" to i8*
  %".27" = call i32 (i8*, ...) @"printf"(i8* %".26", i8* %"boolstr")
  %"load_a.4" = load i32, i32* %"a"
  %"load_b.5" = load i32, i32* %"b"
  %"cmptmp" = icmp slt i32 %"load_a.4", %"load_b.5"
  br i1 %"cmptmp", label %"entry.if", label %"entry.else"
entry.if:
  %"load_a.5" = load i32, i32* %"a"
  %".29" = bitcast [4 x i8]* @"fmt_10" to i8*
  %".30" = call i32 (i8*, ...) @"printf"(i8* %".29", i32 %"load_a.5")
  br label %"entry.endif"
entry.else:
  %"load_b.6" = load i32, i32* %"b"
  %".32" = bitcast [4 x i8]* @"fmt_11" to i8*
  %".33" = call i32 (i8*, ...) @"printf"(i8* %".32", i32 %"load_b.6")
  br label %"entry.endif"
entry.endif:
  %"load_a.6" = load i32, i32* %"a"
  %"cmptmp.1" = icmp eq i32 %"load_a.6", 5
  br i1 %"cmptmp.1", label %"entry.endif.if", label %"entry.endif.endif"
entry.endif.if:
  %"load_a.7" = load i32, i32* %"a"
  %".36" = bitcast [4 x i8]* @"fmt_12" to i8*
  %".37" = call i32 (i8*, ...) @"printf"(i8* %".36", i32 %"load_a.7")
  br label %"entry.endif.endif"
entry.endif.endif:
  %"load_a.8" = load i32, i32* %"a"
  %"load_b.7" = load i32, i32* %"b"
  %"cmptmp.2" = icmp slt i32 %"load_a.8", %"load_b.7"
  %"load_b.8" = load i32, i32* %"b"
  %"cmptmp.3" = icmp eq i32 %"load_b.8", 10
  %"andtmp" = and i1 %"cmptmp.2", %"cmptmp.3"
  br i1 %"andtmp", label %"entry.endif.endif.if", label %"entry.endif.endif.endif"
entry.endif.endif.if:
  %".40" = bitcast [4 x i8]* @"fmt_13" to i8*
  %".41" = call i32 (i8*, ...) @"printf"(i8* %".40", i32 1)
  br label %"entry.endif.endif.endif"
entry.endif.endif.endif:
  %"i" = alloca i32
  store i32 1, i32* %"i"
  br label %"while_header"
while_header:
  %"load_i" = load i32, i32* %"i"
  %"cmptmp.4" = icmp slt i32 %"load_i", 4
  br i1 %"cmptmp.4", label %"while_body", label %"while_exit"
while_body:
  %"load_i.1" = load i32, i32* %"i"
  %".46" = bitcast [4 x i8]* @"fmt_14" to i8*
  %".47" = call i32 (i8*, ...) @"printf"(i8* %".46", i32 %"load_i.1")
  %"load_i.2" = load i32, i32* %"i"
  %"sumtmp.1" = add i32 %"load_i.2", 1
  store i32 %"sumtmp.1", i32* %"i"
  br label %"while_header"
while_exit:
  ret void
}

declare i32 @"printf"(i8* %".1", ...)

@"fmt_1" = internal constant [4 x i8] c"%d\0a\00"
@"fmt_2" = internal constant [4 x i8] c"%d\0a\00"
@"fmt_3" = internal constant [4 x i8] c"%d\0a\00"
@"fmt_4" = internal constant [4 x i8] c"%d\0a\00"
@"fmt_5" = internal constant [4 x i8] c"%d\0a\00"
@"fmt_6" = internal constant [4 x i8] c"%f\0a\00"
@"fmt_7" = internal constant [4 x i8] c"%d\0a\00"
@"str_1" = internal constant [17 x i8] c"Hello, NovaLang!\00"
@"fmt_8" = internal constant [4 x i8] c"%s\0a\00"
@"str_2" = internal constant [5 x i8] c"true\00"
@"str_3" = internal constant [6 x i8] c"false\00"
@"fmt_9" = internal constant [4 x i8] c"%s\0a\00"
@"fmt_10" = internal constant [4 x i8] c"%d\0a\00"
@"fmt_11" = internal constant [4 x i8] c"%d\0a\00"
@"fmt_12" = internal constant [4 x i8] c"%d\0a\00"
@"fmt_13" = internal constant [4 x i8] c"%d\0a\00"
@"fmt_14" = internal constant [4 x i8] c"%d\0a\00"