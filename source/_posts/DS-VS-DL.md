---
title: 延迟渲染Vs延迟光照
layout: DS-VS-DL
toc: true
top: true
date: 2021/12/13 11:23:29
---

原文：[http://www.realtimerendering.com/blog/deferred-lighting-approaches/](http://www.realtimerendering.com/blog/deferred-lighting-approaches/)

鉴于传统的Forward Rendering对于多光源渲染时的低效问题，各种Deferred Rendering的方法被提出并且广泛使用。比如Deferred Shading以及其之后的Deferred Lighting。Deferred方法相对于传统Forward Rendering最主要区别都是提高了对多光源渲染时的效率，它是是将光源的计算转到屏幕空间来进行，进而不浪费无效的光源着色。Deferred Rendering的方法已经已经成为现在游戏引擎的主流。但是，Deferred Shading与Deferred Lighting又是有所不同的：Deferred Shadign是一股脑儿将所有的Shading全部转到Deferred阶段进行，而Deferred Lighting 则是有选择地只将Lighting转到deferred中进行，两种方法的不同也就导致了算法的不同的特点及各自的优劣。关于这一点自己以前一直搞的不是很清楚，最近又搜罗资料学习了一会，这里小总结一下。

传统的Forward Rendering在外理多光源时基本上需要一个与光源数量及待绘制物体数量相关密切相关的复杂程度，这样就导致效率很低。而Deferred Rendering就是将这种与光源相关的计算转到屏幕空间来进行，这样最大程度上减少无关的计算浪费。为了将传统的Forward Rendering转移到Deferred上进行操作需要对光照方程进行分析或改动，并生成相应所需的辅助Buffer来完成最终的着色操作。

Deferred Shading<br />首先，来看一下常见的光照着色方程，其形式如下：<br />![image.png](assets/post_images/DS-VS-DL/image_000.png#clientId=u7c653a43-42d2-4&from=paste&height=88&id=u89429d3a&originHeight=132&originWidth=754&originalType=binary&ratio=1&rotation=0&showTitle=false&size=25349&status=done&style=none&taskId=u3c7c7d69-bc9d-4e08-a1b1-b0c88903b7b&title=&width=502.6666666666667)

其中的

BLK为当前Pixel处的光密度或颜色<br />lk为当前Pixel处的光线向量<br />v为当前Pixel处的视线方向<br />n为当前Pixel处的法向量<br />cdiff为当前Pixel处的diffuse color<br />cspec为当前Pixel处的specular color<br />m为当前Pixel处的specular相关系数<br />对于每个Pixel，使用上式计算出每个光源对其的影响并做累加和即可得到其最终的着色color。因此，如果有了上式中所需的几个必要元素就可以完成对要渲染物体的正确着色，而得到这些基本元素就是Deferred Shading的G-Pass所要完成的操作，DS中的G-Buffer一般来说包含以下基本信息：

Depth<br />Normal & Specular<br />Diffuse albedo<br />Specular albedo<br />Emissive albedo<br />当然，这些是基本的信息，具体的细节及G-Buffer的详细组织跟引擎的结构密切相关，但是有些基本信息是必需要，比如Depth，Normal，Diffuse，Specular等。有了G-Buffer之后即可通过第二个Deferred Pass并且使用G-Buffer 中的信息来完成最终的着色。

但是从上述G-Buffer所包含的必要信息可以看出，用一个那怕是最大空间的Render target也不能包含全部必要所需，而至少需要两个。这在硬件没有MRT支持的情况下就意味着多个Pass，这种情况下效率较传统的Forward rendering不会高太多，因而在没有MRT出现之前该方法在Real-time的渲染中用的并不多。而有了MRT之后其所对应的另外一个问题就是多个Buffer所带来的空间占用，这也是陏后Deffered Lighting在DS基础上出现的一个原因之一。

Deferred Lighting<br />由DS中的G-Buffer可以看出，其中的有两个信息需要占用相应的RT空间，Diffuse albedo和Specular albedo，而Defferd Lighting的改进就是将这两部分从DS的G-Buffer中去掉，而只在Deferred阶段做相应的光照计算，Diffuse与Specular分量影响的计算则是在最终的Shading阶段来进行，因而，DL相对于DS其实增加了一个最终Shading的阶段。DL中之所以能将光照与最终的着色分解需要对原始的着色方程进行如下述调整：

![image.png](assets/post_images/DS-VS-DL/image_001.png#clientId=u7c653a43-42d2-4&from=paste&height=109&id=u8586ad9b&originHeight=164&originWidth=1125&originalType=binary&ratio=1&rotation=0&showTitle=false&size=39131&status=done&style=none&taskId=udd209439-fd6d-47b1-b476-be73ab63f52&title=&width=750)

当然，如果在DS中使用了更复杂的着色模型，可能就需要根据具体情况对上式做不同的改动，以便于各个Pass间的独立。

DL的主要流程为：

准备G-Buffer(Normal&Depth)<br />进行Deferred Lighting并得到L-Buffer(即计算得到上式中的fdiff及fspec)<br />在L-Buffer的基础上重新渲染场景并进行最终的Shading<br />DS vs DL<br />通过上述描述基本上可以看出DS与DL的主要区别：

DS需要更大的G-Buffer来完成对Deferred阶段的前期准备，而且需要硬件有MRT的支持，可以说是硬件要求更高。<br />DL需要两个几何体元的绘制过程来来完成整个渲染操作：G-Pass与Shading pass。这个既是劣势也是优势：由于DS中的Deffered阶段是在完全基本G-Buffer的屏幕空间进行，这也导致了物体材质信息的缺失，这样在处理多变的渲染风格时就需要额外的操作；而DL却可以在Shading阶段得到物体的材质信息进而使这一问题的处理变得较简单。<br />两种方法的上述操作均是只能完成对不透明物体的渲染，而透明或半透明的物体则需额外的传统Pass来完成。<br />关于两种方法更加详细的对比，这里有篇文章做了具体的分析，而且有Wolfgang参与到其中的讨论，可以看看（但是感觉作者可能对DL存在偏见）。

Inferred Lighting<br />在09年的Siggraph上有哥们提出了Inferred Lighting，这个其实是在Deferred Lighting上的一个改进，虽说最终的效能并没有比DL更好，但至少提出了一个新的思路，其主要有以下几个特点：

在G-Buffer中除了基本的Depth、Normal之外增加了叫Discountinuity sensitive filter(DSF)的额外信息，这个其实是对场景中的物体作一个标识、并且组合上Normal的分布得到的一个ID信息，以便在最终的Shading阶段使用。这里的G-Buffer有一个很重要的特点就是可以比正常的屏幕空间小，这样在deferred lighting阶段就会减少需要light 的pixel的数量，进需提高了该阶段的效率；但是带来的影响就是需要在Shading pass中做Up-sampling（G-Buffer中的DSF就是来辅助解决US中遇到的一些问题）。<br />基于G-Buffer的屏幕空间的deferred lighting(比正常的屏幕空间小)并得到L-Buffer。<br />Shading pass中做Up-samping时使用DSF来解决不同物体间的gap。同时，使用DSF并结合G-pass中对半透明物体的Stipple标记方法，就可以在正常的Shading pass中以正常的方法来渲染半透明的物体，个人感觉这个想法不错。<br />不过整体来说Inferred Lighting的效率还是需要改进的（上面的那篇文章里边作者也有提到），但是细节也不复杂，回头实现一下。<br />[<br />](https://blog.csdn.net/BugRunner/article/details/7436600)
