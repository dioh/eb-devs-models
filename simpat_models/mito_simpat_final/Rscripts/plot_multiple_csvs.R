require(tidyverse)
require(scales)

read_and_plot = function(filename){
  
  flocks = read_csv(filename)
  
  title2 = str_remove_all(filename, "/.*?_|.csv")
    
  flocks$t = flocks$t + 1.5
  flocks %>%   filter(t %% 10 == 0) %>% #t %% floor(100/2) == 0 & t < 101)  %>% # & t < 20) %>% 
    #mutate(t=dplyr::recode(t, `0` = " INITIAL STATE", `100`="FINAL STATE")) %>% 
    ggplot(data=., 
           aes(x=x, y=y, color=as.factor(cluster))) + #geom_point() + 
    # geom_point(size=1)+
    geom_segment(aes(x = x, y=y,
                    xend=x+cos(heading),
                    yend=y+sin(heading)),
                arrow = arrow(length = unit(0.02, "npc"))) +
    facet_wrap( ~ t, ncol=4) + 
    scale_x_continuous(breaks=pretty_breaks(n=10)) + 
    scale_y_continuous(breaks=pretty_breaks(n=10)) + 
    # stat_ellipse() +
    theme(legend.position="none") + ggtitle(title2)
  
  "~/proj/crazydevs/plots/" %>% paste(title2, sep="/") %>%
    paste("space_plot.png", sep="_") %>% ggsave()
  
  ####################3
  
    flock_con_clu = flocks %>% add_column(tbin = cut_interval(.$t, 10)) %>% group_by(t) %>%
    mutate(nclusters = n_distinct(cluster)) %>% ungroup() %>%
    group_by(t, cluster) %>%
    mutate(nbirds=n_distinct(bird)) %>% ungroup() %>%
    group_by(t) %>% mutate(nmbirds=mean(nbirds), sdbirds=sd(nbirds))
  
  flock_con_clu %>% ggplot(data=., aes(x=t)) +
    geom_point(aes(y=nclusters), colour="blue", size=0.8)  +
    stat_summary(aes(y=nbirds), fun.data = "mean_sdl", 
                 fun.args = list(mult=1), geom='crossbar', color="gray") +
    geom_point(aes(y=nmbirds), colour="orange", size=0.8) + ylab("number of clusters") +
    scale_y_continuous(sec.axis = sec_axis(~., name = "mean number of birds per cluster")) + ggtitle(title2)
  "~/proj/crazydevs/plots/" %>% paste(title2, sep="/") %>%  paste("clusters_sizes_plot.png", sep="_") %>% ggsave()
  
}

fs::dir_ls("~/proj/crazydevs/results/", regexp = "exp_.*.csv") %>%
  walk(read_and_plot)
