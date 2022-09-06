# **graph-based-code-modelling**

## 介绍

从C#项目中针对变量结点提取数据集。

改写自[microsoft/graph-based-code-modelling: Code for "Generative Code Modeling with Graphs" (ICLR'19) (github.com)](https://github.com/microsoft/graph-based-code-modelling)。

This is the code required to reproduce experiments in two of our papers on modeling of programs, composed of three major components:

- A C# program required to extract (simplified) program graphs from C# source files, similar to our ICLR'18 paper [Learning to Represent Programs with Graphs](https://openreview.net/forum?id=BJOFETxR-). More precisely, it implements that paper apart from the speculative dataflow component ("draw dataflow edges as if a variable would be used in this place") and the alias analysis to filter equivalent variables.
- A TensorFlow model for program graphs, following ICLR'18 paper [Learning to Represent Programs with Graphs](https://openreview.net/forum?id=BJOFETxR-). This is a refactoring/partial rewrite of the original model, incorporating some new ideas on the representation of node labels from Cvitkovic et al. ([Open Vocabulary Learning on Source Code with a Graph-Structured Cache](https://arxiv.org/abs/1810.08305)).
- A TensorFlow model to generate new source code expressions conditional on their context, implementing our ICLR'19 paper [Generative Code Modeling with Graphs](https://openreview.net/forum?id=Bke4KsA5FX).

## 编译运行条件

Windows下，下载Visual Studio 2022、NET 6.0和NuGet安装包，下载后双击安装包安装即可。NuGet安装完成后，需运行指令使其版本达到最新：nuget update -self。

## 编译

下载nuget.exe并添加环境变量，在vs中使用nuget包管理工具将依赖更新至最新，设置编译选项为Debug，右键ExpressionDataExtractor，点击重新生成，即可得到目标程序ExpressionDataExtractor\bin\Debug\net472\ExpressionDataExtractor.exe（编译选项设置为Release则得到ExpressionDataExtractor\bin\Release\net472\ExpressionDataExtractor.exe）。

## 运行

```bat
.\ExpressionDataExtractor\bin\Debug\net472\ExpressionDataExtractor.exe <dataPath> <outputGraphPath> <outputTypeHierPath>
```

如：

```bat
.\ExpressionDataExtractor\bin\Debug\net472\ExpressionDataExtractor.exe E:\TestProject\ E:\output\ E:\output\hide\
.\ExpressionDataExtractor\bin\Debug\net472\ExpressionDataExtractor.exe D:\总要删的\并查集\ E:\output\ E:\output\hide\
```




