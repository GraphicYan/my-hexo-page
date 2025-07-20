---
title: C++生成蓝图的参数类型记录
layout: C2BP-Params
toc: true
tag: UE
date: 2022/10/08 11:23:25
---

<a name="v7pwk"></a>
### 1. 普通参数
在UE C++中寻常函数传参为<br />UFUNCTION(BlueprintCallable) static void Func1(FString InputStr); <br />![](assets/post_images/C2BP-Params/image_000.webp#clientId=ud73c582b-a00b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=uc986a443&margin=%5Bobject%20Object%5D&originHeight=108&originWidth=179&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=u328dd364-5285-474d-aa34-0cf2f65f8e7&title=)
<a name="fhmlg"></a>
### 2. 多输出引脚
但是在UE4的C++中，不带Const的引用在蓝图中是默认为输出引脚的，所以可以借此来实现蓝图的多引脚输出。<br />UFUNCTION(BlueprintCallable) static void Func2(FString& OutputStr); <br />具体蓝图节点如下<br />![](assets/post_images/C2BP-Params/image_001.webp#clientId=ud73c582b-a00b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=u3be3db88&margin=%5Bobject%20Object%5D&originHeight=106&originWidth=159&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=ubff98170-32b4-462f-b84f-2fe068875b6&title=)<br />在虚幻官方的蓝图文档中<br />”在带大量返回参数的函数和返回结构体的函数之间优先前者。“

所以返回大量参数的优先级更高，可以使用Type& Value的方法，使蓝图节点返回大量的参数。<br />甚至还能使用对**指针的引用**来返回更多的参数（感觉挺邪门）<br />UFUNCTION(BlueprintCallable) static AActor* Func5(AActor *& A1, AActor *& A2, AActor *& A3) <br />![](assets/post_images/C2BP-Params/image_002.webp#clientId=ud73c582b-a00b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=u71fb09ce&margin=%5Bobject%20Object%5D&originHeight=184&originWidth=177&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=u0e32d6c7-1c4e-4aa6-8893-66b657f126d&title=)
<a name="JECjk"></a>
### 3. 带Const的引用
一旦引用带有const，那么他将会变为传入的参数<br />UFUNCTION(BlueprintCallable) static void Func3(const FString& ConstInputStr,                   const FVector& ConstInputVector,                   const int32& ConstInputInteger ) {    // ConstInputStr = TEXT("他不行呀");    // ConstInputVector = FVector::ZeroVector } <br />![](assets/post_images/C2BP-Params/image_003.webp#clientId=ud73c582b-a00b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=u6e4f4bdc&margin=%5Bobject%20Object%5D&originHeight=209&originWidth=681&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=ubcbe71ac-eb80-4fad-b32a-296f9070803&title=)<br />FString并不会使用引用，具体也不太清楚为什么！
<a name="aUkBj"></a>
### 4. C++到蓝图真正的引用
使用UPARAM(ref)来作为修饰<br />UFUNCTION(BlueprintCallable) static void Func4(UPARAM(ref) FString& InputStrByRef,                   UPARAM(ref) FVector& InputVector) {    InputStrByRef = TEXT("Hi");    InputVector = FVector::ZeroVector; } <br />![](assets/post_images/C2BP-Params/image_004.webp#clientId=ud73c582b-a00b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=u32e50e6e&margin=%5Bobject%20Object%5D&originHeight=132&originWidth=180&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=u2c08d464-817a-4462-b298-7e850a94d7f&title=)<br />对传入的引用进行值得修改<br />![](assets/post_images/C2BP-Params/image_005.webp#clientId=ud73c582b-a00b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=ucec97d6d&margin=%5Bobject%20Object%5D&originHeight=455&originWidth=720&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=u5574e1d7-db0b-417e-9d9f-c0786feecd2&title=)<br />运行结果为：<br />![](assets/post_images/C2BP-Params/image_006.webp#clientId=ud73c582b-a00b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=u79d9b038&margin=%5Bobject%20Object%5D&originHeight=81&originWidth=315&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=u5f5c35b7-a2ab-4ffd-9673-e71a410ecd2&title=)
<a name="EISxj"></a>
### 5. 最后来个大杂烩
UFUNCTION(BlueprintCallable) static FVector Func(FVector Input,                     FVector& Output,                     const FVector& ConstInputRef,                     UPARAM(ref) FVector& InputRef) {    return FVector::ZeroVector; } <br />![](assets/post_images/C2BP-Params/image_007.webp#clientId=ud73c582b-a00b-4&crop=0&crop=0&crop=1&crop=1&from=paste&id=u9c444f62&margin=%5Bobject%20Object%5D&originHeight=185&originWidth=332&originalType=url&ratio=1&rotation=0&showTitle=false&status=done&style=none&taskId=udd2ad21f-15cb-427b-bf4c-647effb33b0&title=)
