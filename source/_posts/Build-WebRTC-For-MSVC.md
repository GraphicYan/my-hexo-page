---
title: 编译可以在MSVC中使用的WebRTC库
layout: Build-WebRTC-For-MSVC
toc: true
tag: 3D Engine
date: 2023/05/21 22:33:15
---




### 写在前面
相对于移动端，在Windows下使用WebRTC库确实困难些。在移动端（iOS、Andorid），我们可以直接从Google提供的Pod库中拉取编译好的WebRTC库，而在Windows端则需要我们自己编译WebRTC库，并导出WebRTC头文件。<br />这几天手头云渲染推流的工作忙的差不多了，今天就花点时间整理一下这方面的知识，在windows上编译WebRTC静态库，并在MSVC编译器（Visual Studio）里使用它。<br />
由于WebRTC是google在维护的开源网络库，其编译和代码都需要用google对应的ninja、gn和源码管理工具。源码大家可以自行google下载这里就不写了。 ninja相当于一个cmake文件，它将生成用于gn gen编译的模板。 在gn编译时，编译参数需要注意，尤其是其中的 **openSSL库** ，如果你要开发的工程中的已经使用了其他版本的openSSL库（大概率），那你一定不要忘了将编译参数以及ninja文件中对应的**boringSSL**相关的选项换成你的openSSL的。 因为google用的是自己的bringSSL来代替openSSL，说是基于openSSL修改了一些东西，但它的引入会导致与原生openSSL的冲突。

<a name="pqW4l"></a>
### 编译参数
<a name="ehXoW"></a>

以下先从ninja编译时的参数模板展开, 我们以使用UE里的openSSL库代替为例：

<a name="WzSnr"></a>
#### Use UE openSSL
**Release**<br /> gn gen out/release_x64_ssl_ue --target=x64 --ide=vs2019 --sln=webrtc --args="use_lld=false is_debug=false is_clang=false  rtc_builtin_ssl_root_certificates = false rtc_build_ssl=false  rtc_ssl_root=\"D:\UnrealEngine\UnrealEngine-5.1.1-release\Engine\Source\ThirdParty\OpenSSL\1.1.1n\include\Win64\VS2015\"     rtc_build_tools=false rtc_include_tests=false rtc_build_examples=false use_rtti=true rtc_include_internal_audio_device=false"  <br />**Debug**<br /> gn gen out/debug_x64_ssl_ue --target=x64 --ide=vs2019 --sln=webrtc --args="use_lld=false is_debug=true is_clang=false  rtc_builtin_ssl_root_certificates = false rtc_build_ssl=false  rtc_ssl_root=\"D:\UnrealEngine\UnrealEngine-5.1.1-release\Engine\Source\ThirdParty\OpenSSL\1.1.1n\include\Win64\VS2015\"   rtc_build_tools=false rtc_include_tests=false rtc_build_examples=false use_rtti=true rtc_include_internal_audio_device=false"  

<a name="id2NM"></a>
### 修改生成的ninja
匹配表达式： [a-z/_]*boringssl[a-z/_\.0-9-]*<br />将 Include路径替换：<br />D$:/YOUR_OPENSSL_PATH/include<br />将Lib路径替换：<br />D$:/YOUR_OPENSSL_PATH/lib/libssl.lib D$:/YOUR_OPENSSL_PATH/lib/libcrypto.lib


<a name="pwFl8"></a>
# [webrtc编译，不使用内置boringssl，使用openssl的](https://www.cnblogs.com/chai51/p/16324943.html)
<a name="Un6TG"></a>
# 前言
在项目开发过程中，会遇到使用https、TLS、DTLS等场景，这些第三方库一般会使用openssl作为加密套件。例如，qt中加密套件就会使用openssl，但是webrtc会默认使用boringssl；因为boringssl是从openssl创建的分支，两个库同时使用会出现重定义。
<a name="FV0e4"></a>
# 一.验证通过的版本
webrtc版本为m96<br />vs2019
<a name="IK36i"></a>
# 二.生成sln工程
gn gen out/Release --ide=vs2019 --args="use_custom_libcxx=false is_debug=false target_cpu=\"x64\" is_clang=true proprietary_codecs=true treat_warnings_as_errors=false rtc_include_tests=false rtc_enable_protobuf=false rtc_use_h264=true use_rtti=true rtc_build_ssl=false rtc_ssl_root=\"D:/Qt/Tools/OpenSSL/Win_x64/include\""
<a name="YHbDN"></a>
# 三.修改工程文件
编辑 **out/Release/obj/webrtc.ninja**<br />删除正则表达匹配的内容 [a-z/_]*boringssl[a-z/_\.0-9-]*<br />编辑 **out/Release/obj/third_party/libsrtp/libsrtp.ninja**<br />匹配 [a-z/_]*boringssl[a-z/_\.0-9-]*为分别将<br />**include_dirs**匹配替换为 **-ID$:/Qt/Tools/OpenSSL/Win_x64/include**<br />**build**匹配替换为 **D$:/Qt/Tools/OpenSSL/Win_x64/lib/libssl.lib**
<a name="s70xu"></a>
# 四.开始编译
双击打开**out/Release/all.sln**<br />加载完成之后，在**vs2019**中找到**src/webrtc**项目进行编译，这个过程比较漫长<br />编译完成后会在**out/Release/obj/**目录生成**webrtc.lib**文件
<a name="ZYN5I"></a>
## 安装开发环境
在Windows下开发应用程序最常用的开发工具还是Visual Studio，你可以使用VS2019，也可以使用VS2022，目前我还是建议大家先用 VS2019，再等个半年、一年的换VS2022比较合适。VS2019的下载地址[在这里](https://visualstudio.microsoft.com/zh-hans/thank-you-downloading-visual-studio/?sku=community&rel=16&utm_medium=microsoft&utm_campaign=download+from+relnotes&utm_content=vs2019ga+button)，将 VS Installer下载好后，在CMD窗口中执行下面的命令即可。

| ```
$ PATH_TO_INSTALLER.EXE ^
--add Microsoft.VisualStudio.Workload.NativeDesktop ^
--add Microsoft.VisualStudio.Component.VC.ATLMFC ^
--includeRecommended
```
 |
| --- |

当然，正常情况下你在配置WebRTC编译环境时就应该已经将VS安装好了。
<a name="trXHD"></a>
## 编译WebRTC
开发环境安装好后，下面我们就该编译WebRTC源码了。WebRTC源码的下载与编译请看[这篇文章](https://avdancedu.com/2bafd6cf/)。<br />需要注意的是，我们在新项目中引入的WebRTC库，不能直接用下面的命令进行编译：

| ```
gn gen out/Default
ninja -C out/Default
```
 |
| --- |

而必须明确指明编译出的WebRTC是**Debug**版本，还是**Release**版本；是**x86**版本还是**x64**版本……<br />因此，应该使用下面的命令编译WebRTC:

| ```
gn gen --target=x64 --ide=vs2019 --args="is_debug=true rtc_enable_protobuf=false is_clang=false target_cpu=\"x64\"  enable_iterator_debugging=true  use_custom_libcxx=false symbol_level=0 rtc_include_tests=false" out/debug_x64
ninja - C out/debug_x64
```
 |
| --- |

上述 **gn** 中的几个参数含义如下：

- –target，顾名思义，生成x64版本的WebRTC库
- –ide，生成VS工程文件
- –args，编译时的一些配置参数
   - is_debug，为true编译出Debug版本；为false编译出Release版本
   - rtc_enable_protobuf，是否使用protobuf，使用可将其设置为true
   - use_custom_libcxx，WebRTC默认使用的是libc++库，而我们在Windows上使用的是libstdc++库，所以需要将其设置为false
   - symbol_level，编译出的WebRTC库是否带符号表，这个数据量很大，会影响运行速度，所以一般设置为0，表示编译出的WebRTC不带符号表
   - rtc_include_tests，编译WebRTC时是否编译测试用例，如果为false则不编译，这样可以大大加快WebRTC的编译速度

执行上面的命令时，会花一些时间，因此我们需要让**子弹飞一会儿**……
<a name="saCHd"></a>
## 构建自己的应用程序
如果顺利的话，你现在应该已经将WebRTC库编译好了。接下来我们来创建自己的应用程序。<br />为了方便，你可以将WebRTC examples中的peerconnection_client代码拿出来构建一个新的工程，之后再将前面编译好的WebRTC库引入进来，**如果它可以正常运行就达到了我们的目标**。<br />为了达到这个目标，首先我们先使用VS创建一个空项目，步骤如下：

- 第一步，打开Visual Studio，**创建新项目**<br />![](assets/post_images/Build-WebRTC-For-MSVC/image_000.png#clientId=uc50a42e0-7134-4&from=paste&id=u15e3fe10&originHeight=850&originWidth=1280&originalType=url&ratio=1.25&rotation=0&showTitle=false&status=done&style=none&taskId=u16c9fe99-fc1f-4c49-b394-b30dd4bd227&title=)
- 第二步，使用Windows桌面向导创建Windows空项目<br />![](assets/post_images/Build-WebRTC-For-MSVC/image_001.png#clientId=uc50a42e0-7134-4&from=paste&id=u92964c57&originHeight=850&originWidth=1280&originalType=url&ratio=1.25&rotation=0&showTitle=false&status=done&style=none&taskId=uc172fa8b-f789-418d-bf0c-ee49a4aec72&title=)
- 第三步，填写项目名称，并将项目与解决方案放在同一目录下<br />![](assets/post_images/Build-WebRTC-For-MSVC/image_002.png#clientId=uc50a42e0-7134-4&from=paste&id=u90f400be&originHeight=850&originWidth=1280&originalType=url&ratio=1.25&rotation=0&showTitle=false&status=done&style=none&taskId=ud0c46526-8e11-4aee-88d4-11e9b36ea86&title=)
- 第四步，选择应用程序类型为**桌面应用程序**<br />![](assets/post_images/Build-WebRTC-For-MSVC/image_003.png#clientId=uc50a42e0-7134-4&from=paste&id=u712d9e39&originHeight=664&originWidth=625&originalType=url&ratio=1.25&rotation=0&showTitle=false&status=done&style=none&taskId=u6e90d6b6-aed4-47fb-bf45-08a083bc152&title=)
- 第五步，同时勾选**空项目**<br />![](assets/post_images/Build-WebRTC-For-MSVC/image_004.png#clientId=uc50a42e0-7134-4&from=paste&id=ud4067588&originHeight=604&originWidth=625&originalType=url&ratio=1.25&rotation=0&showTitle=false&status=done&style=none&taskId=u846faa51-4a4a-40cb-a8cb-05769cb995d&title=)

至此，我们就构建出了一个VS**空项目**，它里边没有任何文件，如下图所示：<br />![](assets/post_images/Build-WebRTC-For-MSVC/image_005.png#clientId=uc50a42e0-7134-4&from=paste&id=ub37f8531&originHeight=1231&originWidth=1533&originalType=url&ratio=1.25&rotation=0&showTitle=false&status=done&style=none&taskId=u93b8f521-9e88-44e7-8b6e-87ce340413b&title=)<br />空项目创建好后，紧接着我们来移植peerconnection_client代码到新项目中，步骤如下：

- 第一步，从WebRTC源码中拷贝peerconnection_client中的代码到新项目的目录中，在我这里是<br />将C:\webrtc\webrtc-checkout\src\exmaples\peerconnection\client目录中的代码拷贝到C:\Users\lichao\sourceMyWebRTCDemo目录下。如下图所示：![](assets/post_images/Build-WebRTC-For-MSVC/image_006.png#clientId=uc50a42e0-7134-4&from=paste&id=u5d282e59&originHeight=793&originWidth=1408&originalType=url&ratio=1.25&rotation=0&showTitle=false&status=done&style=none&taskId=u6571eb6b-eea7-41db-86a7-4488ecce0ef&title=)![](assets/post_images/Build-WebRTC-For-MSVC/image_007.png#clientId=uc50a42e0-7134-4&from=paste&id=u9784e0d1&originHeight=793&originWidth=1408&originalType=url&ratio=1.25&rotation=0&showTitle=false&status=done&style=none&taskId=uad87597d-c560-4f39-ae90-dfb03f17433&title=)
- 第二步，将新项目中的代码**拖**到VS项目中<br />![](assets/post_images/Build-WebRTC-For-MSVC/image_008.png#clientId=uc50a42e0-7134-4&from=paste&id=u78382652&originHeight=1231&originWidth=1533&originalType=url&ratio=1.25&rotation=0&showTitle=false&status=done&style=none&taskId=ucf63e6a1-caba-4ca3-898f-c30715e8ef1&title=)

通过以上步骤我们就将peerconnection_client中的代码移植好了。接下来咱们来看**重头戏**，如何在项目中引入WebRTC库。
<a name="M3KPg"></a>
## 引入WebRTC库
通常我们引入一个外部库只需要两步，**引入库文件和其头文件**。不过，对于WebRTC，更准确的说对于peerconnection_client而言，它需要的不仅仅是WebRTC库，还需要将WebRTC依赖的第三方库加进来，这是大家觉得在Windows下使用WebRTC库比较麻烦的原因。<br />下面咱们就来看一下如何引入WebRTC库吧！
<a name="HxmeY"></a>
### 添加依赖的头文件
我们若想将WebRTC头文件引入到项目中，可以通过下面两种方法引入：

- 方法一，在VS中将WebRTC源码路径添加到**附加包含目录**中。比如我这里将WebRTC源码下载到了C:\webrtc\webrtc-checkout\src目录下，我只需将该路径添加到:中即可，如下图所示：<br />![](assets/post_images/Build-WebRTC-For-MSVC/image_009.png#clientId=uc50a42e0-7134-4&from=paste&id=u47815b54&originHeight=721&originWidth=1262&originalType=url&ratio=1.25&rotation=0&showTitle=false&status=done&style=none&taskId=uff0896ff-44b2-4d72-a1e8-f9a898f5c60&title=)**这种方法的好处是简单方便，坏处是不便于我们将库文件发布给别人使用。**
| ```
1
```
 | ```
项目 -> 属性 -> C/C++ -> 常规 -> 附加包含目录
```
 |
| --- | --- |

- 方法二，我们可以通过[这个脚本](https://avdancevod.oss-cn-beijing.aliyuncs.com/image/article/import_webrtc/extrac_webrtc_headers.bat)将WebRTC中的头文件提取出来。之后与**方法一**一样，将头文件路径添加到**附加包含目录**中即可。需要注意的是，这个脚本下载后，要将其放到WebRTC源码目录**src**的同级目录中，如下图所示：<br />![](assets/post_images/Build-WebRTC-For-MSVC/image_010.png#clientId=uc50a42e0-7134-4&from=paste&id=uc90969e8&originHeight=761&originWidth=1012&originalType=url&ratio=1.25&rotation=0&showTitle=false&status=done&style=none&taskId=u8a152f70-c48c-4817-bf82-37e371b291f&title=)之后打开Windows控制台，并进入到**src**的同级目录中，在CMD窗口中执行extract_webrtc_headers.bat脚本，这样就可以将WebRTC头文件提取出来了，如下图所示：<br />![](assets/post_images/Build-WebRTC-For-MSVC/image_011.png#clientId=uc50a42e0-7134-4&from=paste&id=ua8fad183&originHeight=590&originWidth=994&originalType=url&ratio=1.25&rotation=0&showTitle=false&status=done&style=none&taskId=uf190ae24-0fd4-48cb-adc6-b5af32b011f&title=)**这种方法的优点是方便其他人使用，缺点是抽取头文件需要花一些时间。**

除了添加上面的头文件路径外，我们还需要将下面几个路径添加到**附加包含项目**中：

| ```
C:\webrtc\webrtc-checkout\src\third_party\jsoncpp\generated
C:\webrtc\webrtc-checkout\src\third_party\jsoncpp\source\include
C:\webrtc\webrtc-checkout\src\third_party\libyuv\include
C:\webrtc\webrtc-checkout\src\third_party\abseil-cpp
```
 |
| --- |

<a name="wRmGh"></a>
### 添加依赖的库
头文件添加好后，接下来咱们来添加WebRTC库文件。WebRTC编译好后，你可以在WebRTC源码目录**src**的**out/debug_x64/obj**目录下找到**WebRTC.lib**文件，这就是编译好的WebRTC库。<br />我们将它添加到VS中的**附加库目录**中，具体操作如下：

| ```
右键项目 -> 属性 -> 链接器 -> 常规 -> 附加库目录
```
 |
| --- |

WebRTC库文件路径添加好后，如下图所示：<br />![](assets/post_images/Build-WebRTC-For-MSVC/image_012.png#clientId=uc50a42e0-7134-4&from=paste&id=u52b31581&originHeight=721&originWidth=1262&originalType=url&ratio=1.25&rotation=0&showTitle=false&status=done&style=none&taskId=ufcd0c813-1cf5-4fc2-84da-9ecefddc4b1&title=)<br />接着咱们添加具体的的依赖库，添加依赖库的位置在:

| ```
右键项目 -> 属性 -> 链接器 -> 输入 -> 附加依赖项
```
 |
| --- |

如下图所示：<br />![](assets/post_images/Build-WebRTC-For-MSVC/image_013.png#clientId=uc50a42e0-7134-4&from=paste&id=uace681eb&originHeight=721&originWidth=1262&originalType=url&ratio=1.25&rotation=0&showTitle=false&status=done&style=none&taskId=u95610255-8df4-4f5d-9970-4e0910dc037&title=)<br />具体都依赖哪些依赖项呢？这里我以 **M93(4577)** 为例，对于这个版本的peerconnection_client来说，它需要下面的依赖库：

- WebRTC相关的库包括：
| ```
third_party/abseil-cpp/absl/flags/marshalling/marshalling.obj
third_party/abseil-cpp/absl/flags/program_name/program_name.obj
third_party/abseil-cpp/absl/flags/flag/flag.obj
third_party/abseil-cpp/absl/flags/flag_internal/flag.obj
third_party/abseil-cpp/absl/flags/commandlineflag/commandlineflag.obj
third_party/abseil-cpp/absl/flags/commandlineflag_internal/commandlineflag.obj
third_party/abseil-cpp/absl/flags/private_handle_accessor/private_handle_accessor.obj
third_party/abseil-cpp/absl/flags/reflection/reflection.obj
third_party/abseil-cpp/absl/flags/parse/parse.obj
third_party/abseil-cpp/absl/flags/usage/usage.obj
third_party/abseil-cpp/absl/flags/usage_internal/usage.obj
third_party/abseil-cpp/absl/flags/config/usage_config.obj
third_party/jsoncpp/jsoncpp/json_reader.obj
third_party/jsoncpp/jsoncpp/json_value.obj
third_party/jsoncpp/jsoncpp/json_writer.obj
test/field_trial/field_trial.obj
test/video_test_common/test_video_capturer.obj
test/platform_video_capturer/vcm_capturer.obj
rtc_base/rtc_json/json.obj
```
 |
| --- |

- 系统相关的库包括：
| ```
advapi32.lib
comdlg32.lib
dbghelp.lib
dnsapi.lib
gdi32.lib
msimg32.lib
odbc32.lib
odbccp32.lib
oleaut32.lib
shell32.lib
shlwapi.lib
user32.lib
usp10.lib
uuid.lib
version.lib
wininet.lib
winmm.lib
winspool.lib
ws2_32.lib
delayimp.lib
kernel32.lib
ole32.lib
crypt32.lib
iphlpapi.lib
secur32.lib
dmoguids.lib
wmcodecdspuuid.lib
amstrmid.lib
msdmo.lib
strmiids.lib
```
 |
| --- |

<a name="wvabH"></a>
### 添加宏
除了上面讲的需要引入头文件和WebRTC库之外，还需要添加下面这些宏。这些宏的具体含义我有不介绍了，有兴趣的同学可以自己在网上搜索一下。

| ```
USE_AURA=1
_HAS_NODISCARD
_HAS_EXCEPTIONS=0
__STD_C
_CRT_RAND_S
_CRT_SECURE_NO_DEPRECATE
_SCL_SECURE_NO_DEPRECATE
_ATL_NO_OPENGL
_WINDOWS
CERT_CHAIN_PARA_HAS_EXTRA_FIELDS
PSAPI_VERSION=2
WIN32
_SECURE_ATL
WINAPI_FAMILY=WINAPI_FAMILY_DESKTOP_APP
WIN32_LEAN_AND_MEAN
NOMINMAX
_UNICODE
UNICODE
NTDDI_VERSION=NTDDI_WIN10_VB
_WIN32_WINNT=0x0A00
WINVER=0x0A00
_DEBUG
DYNAMIC_ANNOTATIONS_ENABLED=1
WEBRTC_ENABLE_PROTOBUF=0
WEBRTC_INCLUDE_INTERNAL_AUDIO_DEVICE
RTC_ENABLE_VP9
WEBRTC_HAVE_SCTP
WEBRTC_ENABLE_AVX2
RTC_ENABLE_WIN_WGC
WEBRTC_NON_STATIC_TRACE_EVENT_HANDLERS=0
WEBRTC_WIN
ABSL_ALLOCATOR_NOTHROW=1
_ENABLE_EXTENDED_ALIGNED_STORAGE
ABSL_FLAGS_STRIP_NAMES=0
HAVE_WEBRTC_VIDEO
```
 |
| --- |

添加方法如下:

- 首先在 VS 中执行下面的操作，
| ```
右键项目 -> 属性 -> C/C++ -> 预处理器
```
 |
| --- |

- 之后将上面的宏添加到**预处理器**中即可。
<a name="frx1s"></a>
## 编译运行
到此为止，我们就将peerconnection_client的代码移植好了，直接点![](assets/post_images/Build-WebRTC-For-MSVC/image_014.png#clientId=uc50a42e0-7134-4&from=paste&id=u97525043&originHeight=38&originWidth=34&originalType=url&ratio=1.25&rotation=0&showTitle=false&status=done&style=none&taskId=uf187e82f-4abc-4298-afd4-459f2cd77ff&title=)测试一下吧！<br />此时，编译器有可能报4996的错误，解决该问题办法很简单，只要在

| ```
右键项目项 -> 属性 -> C/C++ -> 高级 -> 禁用特定警告
```
 |
| --- |

中将 **4996** 添加进去即可。除此之外，还有可能遇到 **/MDd** 错误，解决它可以通过在

| ```
右键项目项 -> 属性 -> C/C++ -> 代码生成 -> 运行库
```
 |
| --- |

中将 **/MDd** 改为 **/MTd** 即可。<br />如果一切顺利，peerconnection_client的连接窗口就展示在你面前了，如下图所示。<br />![](assets/post_images/Build-WebRTC-For-MSVC/image_015.png#clientId=uc50a42e0-7134-4&from=paste&id=u9d3008b8&originHeight=827&originWidth=1064&originalType=url&ratio=1.25&rotation=0&showTitle=false&status=done&style=none&taskId=u62a1205a-0807-4fbb-9f86-18fb56e5330&title=)<br />此时，你需要先将peerconnection_server程序运行起来，让它侦听 **8888** 端口；之后在peerconnection_client的连接界面中输入 **127.0.0.1**，点击**连接**，如果能进入列表界面就表明OK了。
