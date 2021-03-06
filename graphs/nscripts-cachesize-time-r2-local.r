#!/usr/bin/env Rscript
# install.packages ('ggplot2')  
library (ggplot2)
# install.packages ('scales')  
library (scales)
# install.packages ('doBy')
library (doBy)
#install.packages('data.table')
library(data.table)
library (plyr)
source("./graphs/summarySE.r")
source("./graphs/graph-style.R")
source("./graphs/variables.r")

print ("Plot variable time curve.")

varx='consperc'
varx2=quote(consperc)

data = read.table ("./temp/summarytime.txt", header=T)
#data$Strategy = factor (data$Strategy)    
#data$TimeSec = factor (data$TimeSec)
 
if (lang == "br")
{
  tit = "Eficiência na Entrega de Dados"
  yl = "Eficiência na Entrega de Dados \n(Pacotes de Dados Recebidos pelo Consumidor / \n Soma de Interesses em Cada Enlace"
  xlb = "Tempo (Segundos)"
}else
{
  tit = "Data Delivery Efficiency"
#  yl = "Data Delivery Efficiency \n(Consumer-Received Data Packets / \n Sum Of Interests Sent On Each Link)"
  yl = "Data Delivery Efficiency"
  xlb = "Time (Seconds)"
}

if (varx2 == "consxint")
{
xl = "Number of Consumer Nodes"
data$consxint <- factor (data$consxint) 
}else if (varx2 == "prodxint")
{
xl = "Number of Producer Nodes"
data$prodxint <- factor (data$prodxint) 
}else if (varx2 == "nprefix")
{
xl = "Number of Prefixes"
data$nprefix <- factor (data$nprefix) 
}else if (varx2 == "consperc")
{
xl = "Probability of Prefix Change (%)"
data$consperc <- factor (data$consperc) 
}else if (varx2 == "topo")
{
xl = "Topology Number of Nodes"
data$topo <- factor (data$topo) 
}else if (varx2 == "rate")
{
xl = "Consumer Interests per Second"
data$rate <- factor (data$rate) 
}else if (varx2 == "hellorate")
{
xl = "Hello Frequency (Hz)"
data$hellorate <- factor (data$hellorate)
}else if (varx2 == "fibsize")
{
xl = "Maximum FIB Size"
data$fibsize <- factor (data$fibsize)
}else if (varx2 == "constime")
{
xl = "Producer Roaming Interval (Seconds)"
data$constime <- factor (data$constime)
}else if (varx2 == "regrate")
{
xl = "Prefix Registration Rate"
data$regrate <- factor (data$regrate)
}else if (varx2 == "script")
{
xl = "Scheme"
data$script <- factor (data$script)
} 


output = summarySE (data, measurevar="ise", groupvars=c("Strategy",paste(varx),"TimeSec") )
print (paste("Output: "))
print (output)

output2 = subset (output, (Strategy != 'Omniscient'))
lttsize=24
pd <- position_dodge(.8)
g.all <- ggplot (output2, aes (x=TimeSec, y=ise, linetype=eval(varx2), shape=Strategy))+ #,color=eval(varx2))) +
  geom_point (size=3) +
  geom_line (size=1) +
#  geom_errorbar (aes(ymin=ise-ci,ymax=ise+ci), width=4, size=1) +  
  ylab (yl) +
  #xlab (xlb) +
  theme_bw() +
  #scale_linetype_discrete(name  = xl) +
  scale_linetype_manual(name = "Routers Cache Size", values=c("solid", "dotdash", "dotted", "dashed", "longdash", "twodash"))+
#  scale_color_discrete(name  = xl) +
#  scale_shape_discrete(name  = "Strategy", solid=FALSE) +
  scale_shape(name  = "Consumers Register Data in Cache", solid=FALSE)+
  theme(legend.position="bottom", text = element_text(family="Times", size = lttsize), legend.title = element_text(family="Times", size = lttsize-6),
  axis.text = element_text(family="Times", size = lttsize), legend.text = element_text(family="Times", size = lttsize-6))
png (paste("./temp/NScriptsCacheSizeTime.png",sep=""), width=500, height=500)
print (g.all)
dev.off ()

