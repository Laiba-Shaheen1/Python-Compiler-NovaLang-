; ModuleID = "nova_module"
target triple = "x86_64-pc-windows-msvc"
target datalayout = ""

define void @"main"()
{
entry:
  %"x" = alloca i32
  store i32 100, i32* %"x"
  %"y" = alloca i32
  store i32 42, i32* %"y"
  %"load_x" = load i32, i32* %"x"
  %"load_y" = load i32, i32* %"y"
  %"subtmp" = sub i32 %"load_x", %"load_y"
  %".4" = bitcast [4 x i8]* @"fmt_1" to i8*
  %".5" = call i32 (i8*, ...) @"printf"(i8* %".4", i32 %"subtmp")
  %"load_x.1" = load i32, i32* %"x"
  %"multmp" = mul i32 %"load_x.1", 2
  %".6" = bitcast [4 x i8]* @"fmt_2" to i8*
  %".7" = call i32 (i8*, ...) @"printf"(i8* %".6", i32 %"multmp")
  %".8" = bitcast [16 x i8]* @"str_1" to i8*
  %".9" = bitcast [4 x i8]* @"fmt_3" to i8*
  %".10" = call i32 (i8*, ...) @"printf"(i8* %".9", i8* %".8")
  %"load_x.2" = load i32, i32* %"x"
  %"load_y.1" = load i32, i32* %"y"
  %"cmptmp" = icmp sgt i32 %"load_x.2", %"load_y.1"
  br i1 %"cmptmp", label %"entry.if", label %"entry.else"
entry.if:
  %".12" = bitcast [4 x i8]* @"fmt_4" to i8*
  %".13" = call i32 (i8*, ...) @"printf"(i8* %".12", i32 1)
  br label %"entry.endif"
entry.else:
  %".15" = bitcast [4 x i8]* @"fmt_5" to i8*
  %".16" = call i32 (i8*, ...) @"printf"(i8* %".15", i32 0)
  br label %"entry.endif"
entry.endif:
  %"i" = alloca i32
  store i32 1, i32* %"i"
  %"load_i" = load i32, i32* %"i"
  %"load_i.1" = load i32, i32* %"i"
  %"load_i.2" = load i32, i32* %"i"
  %"sumtmp" = add i32 %"load_i.2", 1
  store i32 %"sumtmp", i32* %"i"
  br label %"while_header"
while_header:
  %"cmptmp.1" = icmp slt i32 %"load_i", 4
  br i1 %"cmptmp.1", label %"while_body", label %"while_exit"
while_body:
  %".22" = bitcast [4 x i8]* @"fmt_6" to i8*
  %".23" = call i32 (i8*, ...) @"printf"(i8* %".22", i32 %"load_i.1")
  br label %"while_header"
while_exit:
  ret void
}

declare i32 @"printf"(i8* %".1", ...)

@"fmt_1" = internal constant [4 x i8] c"%d\0a\00"
@"fmt_2" = internal constant [4 x i8] c"%d\0a\00"
@"str_1" = internal constant [16 x i8] c"NovaLang works!\00"
@"fmt_3" = internal constant [4 x i8] c"%s\0a\00"
@"fmt_4" = internal constant [4 x i8] c"%d\0a\00"
@"fmt_5" = internal constant [4 x i8] c"%d\0a\00"
@"fmt_6" = internal constant [4 x i8] c"%d\0a\00"