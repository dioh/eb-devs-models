require(scales)
require(ggpubr)
require(ggplot2)
require(tidyverse)

flocks =read_csv("~/proj/crazydevs/results/historial_flocks_g300_r15_d2.0.csv") # Excelente
flocks =read_csv("/tmp/historial_flocks_g70_r3_d1.5.csv") # Excelente pero menos
flocks =read_csv("/tmp/historial_flocks_g70_r5_d1.5_explosivo.csv") # Excelente pero menos


flocks$t = flocks$t + 1.5

flocks %>%   filter(t %% 50 == 0   ) %>% #t %% floor(100/2) == 0 & t < 101)  %>% # & t < 20) %>% 
  #mutate(t=dplyr::recode(t, `0` = " INITIAL STATE", `100`="FINAL STATE")) %>% 
  ggplot(data=., 
         aes(x=x, y=y, color=as.factor(cluster))) + #geom_point() + 
  geom_segment(aes(x = x, y=y, 
                   xend=x+cos(heading), 
                   yend=y+sin(heading)),
               arrow = arrow(length = unit(0.02, "npc"))) +
  facet_wrap( ~ t, ncol=4) + 
  scale_x_continuous(breaks=pretty_breaks(n=10)) + 
  scale_y_continuous(breaks=pretty_breaks(n=10)) + 
  stat_ellipse() +
  theme(legend.position="none")
  

  flocks %>% group_by(t, cluster) %>% summarise(birds = n_distinct(bird)) %>% group_by(t) %>% 
  summarise(max.floc = max(birds)) %>% tail



flocks %>% filter(t %%  60  ==0 ) %>% 
  rbind((flocks %>% filter(bird==37)) %>% transform( t=60)) %>%
  mutate(t=dplyr::recode(t, `0` = " INITIAL STATE: T=0", `60`="FINAL STATE: T=60")) %>% 
  ggplot(data=., 
         aes(x=x, y=y, color=as.factor(clustahi esta por er))) + #geom_point() + 
  geom_segment(aes(x = x, y=y, 
                   xend=x+sin(heading * pi/180), 
                   yend=y+cos(heading * pi/180)),
               arrow = arrow(length = unit(0.02, "npc"))) +
  facet_wrap( ~ t, ncol=4) + stat_ellipse() + 
  scale_x_continuous(breaks=pretty_breaks(n=3)) + 
  scale_y_continuous(breaks=pretty_breaks(n=5)) + 
  theme_minimal() + 
  theme(legend.position="none", 
        panel.spacing = unit(-0.5, "lines"), 
        text = element_text(size=22),
        axis.text = element_text(size=22),
        axis.title = element_text(size=26)) 
+
  ggtitle("Birds direction, position and flock membership evolution")  
  
  (flocks %>% filter(bird==37)) %>% transform(cluster=666 + t, t=60)%>% ggplot(data=., aes(x=x, y=y, color=cluster)) + geom_text(aes(label=t), size=3)




ggsave("~/proj/papers_phd/2018_wsc_ext_abs/flocks.png", width = 16, height = 16/2)


flocks %>% filter(t  ==0 | t == 60) %>% #t %% floor(100/2) == 0 & t < 101)  %>% # & t < 20) %>% 
  rbind((flocks %>% filter(bird==37 | bird==95)) %>% transform(cluster=bird, t=60)) %>%

  mutate(t=dplyr::recode(t, `0` = " INITIAL STATE", `60`="FINAL STATE")) %>% 
  
  ggplot(data=., 
         aes(x=x, y=y, color=as.factor(cluster))) + #geom_point() + 
  geom_segment(aes(x = x, y=y,
                   xend=x+sin(heading * pi/180), 
                   yend=y+cos(heading * pi/180)),
               arrow = arrow(length = unit(0.02, "npc"))) +
  stat_ellipse(data=flocks %>% filter(t  ==0 | t == 60) %>%
                 mutate(t=dplyr::recode(t, `0` = " INITIAL STATE", `60`="FINAL STATE"))) +
  #stat_ellipse() +
  scale_x_continuous(breaks=pretty_breaks(n=3)) + 
  scale_y_continuous(breaks=pretty_breaks(n=5)) + 
  facet_wrap( ~ t, nrow=2) +
    theme_minimal() + 
  theme(legend.position="none", 
        panel.spacing = unit(-0.5, "lines"), text = element_text(size=22))


data.plot = flocks %>% filter(t  %% 15 ==0) #%>% #t %% floor(100/2) == 0 & t < 101)  %>% # & t < 20) %>% 
  mutate(t=(dplyr::recode(t, `0` = " INITIAL STATE", `15`='INTER. STATE 1',
                         `45`='INTER. STATE 2',`60`="FINAL STATE"))) # %>%  
data.plot$tf =  data.plot$t
  factor(data.plot$t, levels=c(" INITIAL STATE", 'INTER. STATE 1', 
                  'INTER. STATE 2',"FINAL STATE")
  )  

data.plot %>% ggplot(data=., 
         aes(x=x, y=y)) + 
  geom_segment(aes(x = x, y=y, color=as.factor(cluster),
                   xend=x+sin(heading), 
                   yend=y+cos(heading)),
               arrow = arrow(length = unit(0.02, "npc"))) +
  stat_ellipse(aes(color=as.factor(cluster))) +
  scale_x_continuous(breaks=pretty_breaks(n=3)) + 
  scale_y_continuous(breaks=pretty_breaks(n=5)) + 
  facet_wrap( . ~ tf, nrow=2) +
  theme_minimal() + 
  theme(legend.position="none", 
        panel.spacing = unit(-0.5, "lines"), text = element_text(size=22)) +
  geom_segment(data=rbind((flocks %>% filter(bird==123 & (t %% 3 ==0)))
                        %>% transform(cluster=500, t=60)) %>%
               mutate(t=dplyr::recode(t, `0` = " INITIAL STATE", `15`='INTER. STATE 1',
                                      `45`='INTER. STATE 2',`60`="FINAL STATE")),
               aes(x = x, y=y, fill="black",
                   xend=x+sin(heading * pi/180), 
                   yend=y+cos(heading * pi/180)),
               arrow = arrow(length = unit(0.02, "npc")
                             ))




ggsave("~/proj/papers_phd/2018_esm_paper/flocks.png", width = 16/2, height = 16)

ggsave("~/proj/papers_phd/2018_esm_paper/flocks.svg", width = 16/2, height = 16)


clusters_threshold = 1
flocks %>% group_by(t, cluster) %>% summarise(pajaritos = n_distinct(bird)) %>%
  mutate(is.small.cluster = pajaritos <= clusters_threshold) %>%
  mutate(is.small.cluster = dplyr::recode(as.numeric(is.small.cluster),
                                          `1` = "SINGLE BIRD",
                                          `0` = "FLOCK SIZE > 1")) %>%
  group_by(t, is.small.cluster) %>%
  mutate(count=n_distinct(cluster)) %>% filter(t < 500) %>% 
  ggplot(data=., aes(x=t, y=count, color=is.small.cluster)) + geom_point() + 
  geom_smooth(method="loess") + #method = "gam", formula = y ~ s(x, bs = "cs")) +
  theme_minimal() + 
    theme(legend.position=c(0.75,0.85),
          legend.title = element_blank(),
          legend.text = element_text(size=18),
          legend.background = element_rect(fill="transparent",colour=NA),
          axis.text = element_text(size=18),
          axis.title = element_text(size=18),
          text = element_text(size=18)) +
  labs(y="Number of clusters", x="Time (s)", color="Cluster size <= 3") +
  scale_x_continuous(breaks=pretty_breaks(n=10)) + xlim(0, 60) + 
  scale_y_continuous(breaks=pretty_breaks(n=10))  

ggsave("~/proj/papers_phd/2018_esm_paper/clusters.png", width = 8, height = 8)

ggsave("/tmp/clusters.png", width = 8, height = 4)


clusters_threshold = 1
 flocks %>% group_by(t, cluster) %>% summarise(pajaritos = n_distinct(bird)) %>%
  # filter(pajaritos > clusters_threshold) %>% ungroup() %>% 
   group_by(t) %>%
   summarise(count=n_distinct(cluster)) %>% filter(t < 500) %>% 
  qplot(data=., x=t, y=count, geom=c("point", "smooth"))  +
  theme_classic() + labs(y="Number of clusters", x="Time (s)") +
  scale_x_continuous(breaks=pretty_breaks(n=10)) + 
   scale_y_continuous(breaks=pretty_breaks(n=10)) +
   theme(text = element_text(size=18)) + ylim(0, 60)# + ggtitle("clusters tamañó > 3")

 flocks %>% group_by(t, cluster) %>% summarise(pajaritos = n_distinct(bird)) %>%
   filter(pajaritos <= clusters_threshold) %>% ungroup() %>% group_by(t) %>%
   summarise(count=n_distinct(cluster)) %>% filter(t < 500) %>% 
   qplot(data=., x=t, y=count, geom=c("point", "smooth"))  +
   theme_classic() + labs(y="Number of clusters", x="Time (s)") +
   scale_x_continuous(breaks=pretty_breaks(n=10)) + 
   scale_y_continuous(breaks=pretty_breaks(n=10)) +
   theme(text = element_text(size=18)) #+ ylim(0, 100) + ggtitle("clusters tamaño <=3")
 
 
 flocks %>% group_by(t, cluster) %>% summarise(pajaritos = n_distinct(bird)) %>% 
   rowwise() %>% mutate(rancho_aparte = pajaritos < 4)  %>% group_by(t, rancho_aparte) %>%
   mutate(dis_clusters = n_distinct(cluster)) %>% ungroup() %>% 
 filter(t %% 20 == 0 ) %>% 
   ggplot(data=., aes(x=as.factor(t), y=pajaritos)) + geom_jitter() +
   geom_violin() + #aes(fill=rancho_aparte)) + 
   geom_text(aes(y=-10,label=dis_clusters)) + 
   #scale_y_log10() +
  # theme_classic() + labs(y="Number of birds per cluster", x="Time (s)") + 
    facet_wrap( ~ rancho_aparte) +
   #scale_y_continuous(breaks=pretty_breaks(n=10)) +
   theme(text = element_text(size=18)) #+ ylim(0, 50) + ggtitle("clusters tamaño <=3")
 
 flocks %>% group_by(t, cluster) %>% summarise(pajaritos = n_distinct(bird)) %>% 
   rowwise() %>% mutate(rancho_aparte = pajaritos < 4)  %>% group_by(t, rancho_aparte) %>%
   mutate(dis_clusters = n_distinct(cluster)) %>% ungroup() %>% 
   filter(t %% 20 == 0 ) %>% 
   ggplot(data=., aes(x=as.factor(t), y=sum(pajaritos))) + geom_jitter() +
 #  geom_violin() + #aes(fill=rancho_aparte)) + 
   geom_text(aes(y=-10,label=dis_clusters)) + 
   #scale_y_log10() +
   # theme_classic() + labs(y="Number of birds per cluster", x="Time (s)") + 
   facet_wrap( ~ rancho_aparte) +
   #scale_y_continuous(breaks=pretty_breaks(n=10)) +
   theme(text = element_text(size=18)) #+ ylim(0, 50) + ggtitle("clusters tamaño <=3")
 
 
 
 flocks %>% filter(t<=60 & heading>=0) %>% mutate(t_interval=cut_interval(t, 10)) %>% 
   qplot(data=., x=t_interval,
         y=heading, geom= c("boxplot")) + 
   theme_minimal() + 
   theme(legend.position=c(0.75,0.85),
         legend.title = element_blank(),
         legend.text = element_text(size=18),
         legend.background = element_rect(fill="transparent",colour=NA),
         axis.text = element_text(size=18),
         axis.text.x = element_text(angle=30, hjust = 1),
         text = element_text(size=18)) +
   labs(y="Direction of the birds in degrees", x="Time (s)") +
   scale_y_continuous(breaks=pretty_breaks(n=7)) 
 
 ggsave("~/proj/papers_phd/2018_esm_paper/directions.png", width = 8, height = 6)
 ggsave("/tmp/directions.png", width = 8, height = 4)
 
 
 
 
 
 
 
 
 
 #---------------------
 
 stat_clip_ellipse <- function(mapping = NULL,
                               geom = "path", position = "identity",
                               ...,
                               type = "t",
                               level = 0.95,
                               segments = 51,
                               na.rm = FALSE,
                               show.legend = NA,
                               inherit.aes = TRUE) {
   layer(
     data = (data %>% filter(bird != 37)),
     mapping = mapping,
     stat = StatEllipse,
     geom = geom,
     position = position,
     show.legend = show.legend,
     inherit.aes = inherit.aes,
     params = list(
       type = type,
       level = level,
       segments = segments,
       na.rm = na.rm,
       ...
     )
   )
 }
 
 
 
 
 flocks %>% #filter(t<= 60) %>% #head(100) %>% 
   mutate(hbin=cut_interval(heading, n=50), tbin=cut_interval(t, n=4)) %>% 
   group_by(hbin, tbin) %>% 
   summarise(freq=n()) %>%
   mutate(
     angle= 
       str_remove_all(
         string = hbin, 
         pattern = "(\\(|\\[)|,.*") %>% as.numeric()) %>%
   ggplot(data=., aes(x=angle, y=freq)) +
   coord_polar(theta = "x", start = 0 * -pi/45) +
   geom_bar(stat = "identity") +
   #scale_y_log10() +
   #scale_x_continuous(breaks = seq(0, 2*pi, 0.1), limits = c(0, 360))  +
   facet_wrap( ~ tbin, ncol=1) +
   theme(legend.position=c(0.75,0.85),
         legend.title = element_blank(),
         legend.text = element_text(size=18),
         legend.background = element_rect(fill="transparent",colour=NA),
         axis.text = element_text(size=18),
         axis.text.x = element_text(angle=0, hjust = 1),
         text = element_text(size=18))  +
   theme_minimal() 
 
 
 flocks %>% filter(t<= 60) %>% #head(100) %>% 
   mutate(hbin=cut_interval(heading, n=10), tbin=cut_interval(t, n=4)) %>% 
   group_by(hbin, tbin) %>% 
   summarise(freq=n()) %>%
   mutate(
     angle= 
       str_remove_all(
         string = hbin, 
         pattern = "(\\(|\\[)|,.*") %>% as.numeric()) %>%
   ggplot(data=., aes(x=angle)) +
   coord_polar(theta = "x", start = 0 * -pi/45) +
   geom_histogram(stat = "density") + #stat = "density") + 
   scale_x_continuous(breaks = seq(0, 360, 20), limits = c(0, 360))  +
   facet_wrap( ~ tbin, nrow=1) +
   theme_minimal() +
   theme(
     legend.position=c(0.75,0.85),
         legend.title = element_blank(),
         legend.text = element_text(size=18),
         legend.background = element_rect(fill="transparent",colour=NA),
         axis.text = element_text(size=18),
         axis.text.x = element_text(angle=30, hjust = 1),
         text = element_text(size=18))  
 
 
 #######################
 
flocks %>% filter(t < 10) %>%  add_column(tbin=cut_interval(.$t, 10)) %>% 
   ggplot(data=., aes(x=heading)) +
   geom_histogram() + facet_wrap( ~ tbin)

  pepe = flocks %>% filter(t>0) %>%  ggplot(data=.,
                          aes(x=x, y=y)) +
  geom_point(aes(x=x, y=y)) + 
   # geom_segment(aes(x = x, y=y,
   #                  color=as.factor(cluster),
   #                  xend=x+cos(heading),
   #                  yend=y+sin(heading)),
   #              arrow = arrow(length = unit(0.01, "npc"))) +
  theme_minimal() + theme(legend.position = 'none') +
   transition_time(t) +   labs(title = 't: {frame_time}') 
animate(pepe, nframes=50, fps=1, duration=1000)
pepa = animate(pepe, fps=1)


flocks %>% group_by(t, cluster) %>% 
  summarise(ssin = sum(sin(heading)), 
            scos=sum(cos(heading)),
            nheading=(atan2(ssin, scos) %% (2*pi))) %>%
  qplot(data=., x=nheading, geom="histogram", facets = t ~ .)



####

flock_con_clu = flocks %>% add_column(tbin = cut_interval(.$t, 10)) %>% group_by(t) %>%
  mutate(nclusters = n_distinct(cluster)) %>% ungroup() %>%
  group_by(t, cluster) %>%
  mutate(nbirds=n_distinct(bird)) %>% ungroup() %>%
  group_by(t) %>% mutate(nmbirds=mean(nbirds))

flock_con_clu %>% ggplot(data=., aes(x=t)) +
  # geom_smooth(aes(y=nclusters, color="red"))  +
  # geom_smooth(aes(y=nbirds)) +
  geom_point(aes(y=nclusters), colour="blue")  +
  geom_point(aes(y=nmbirds), colour="orange") + ylab("number of clusters") +
  scale_y_continuous(sec.axis = sec_axis(~., name = "mean number of birds per cluster"))

