require(ggpubr)
require(clv)
require(scales)
require(ggpubr)
require(ggplot2)
require(tidyverse)

fixdata = function(data) transform(data, cluster = if_else(is.na(cluster), 666, cluster), t = t+1.5)

flocks.vanilla = read_csv("~/proj/crazydevs/pythonpdevs/examples/flocks/results/historial_flocks_g70_r5_d1.5_ac-1_septurn0.03_alignturn0.09_cohturn0.06_supercohere-1.00.csv") %>%
fixdata()
flocks.ba = read_csv("~/proj/crazydevs/pythonpdevs/examples/flocks/results/historial_flocks_g70_r5_d1.5_ac-1_septurn0.03_alignturn0.09_cohturn0.06_supercohere25.00.csv") %>%
  fixdata()
flocks.fa = read_csv("~/proj/crazydevs/pythonpdevs/examples/flocks/results/historial_flocks_g70_r5_d1.5_ac15_septurn0.03_alignturn0.09_cohturn0.06_supercohere-1.00.csv") %>%
fixdata()



plot_clusters <- function(flocks) {
  clusters= flocks %>% filter(t>0) %>% group_by(t, retry) %>% 
    summarise(nclusters = n_distinct(cluster))
  
  ggplot(data=clusters, aes(x=t, y=nclusters)) +
    stat_summary(mapping=aes(fun.y="mean_sd"), geom="crossbar", color='lightgreen', alfa=0.3) +
    stat_summary(mapping=aes(fun.y="mean"), geom="line", color='darkgray') +
    labs(y = "Number of clusters (green)",
         x = "time(s)") +
    theme(text = element_text(size = 14))
}

plot_clusters_agents <- function(flo) {
  clusters= flo %>% filter(t>0) %>% group_by(t, retry) %>% 
    summarise(nclusters = n_distinct(cluster))
  
  agents =  flo %>% filter(t>0) %>% group_by(t, retry, cluster) %>% 
    summarise(nagents = n())
  
  ggplot(data=clusters, aes(x=t, y=nclusters)) +
    stat_summary(mapping=aes(fun.y="mean_sd"), geom="crossbar", color='lightgreen', alfa=0.3) +
    stat_summary(mapping=aes(fun.y="mean"), geom="line", color='darkgray') +
    labs(y = "Number of clusters (green)",
         x = "time(s)") +
      stat_summary(data=agents, inherit.aes = F, 
                 mapping=aes(x=t, y=nagents, 
                             fun.y="mean_sd"), geom="crossbar", color='lightblue', alfa=0.3) +
    stat_summary(data=agents, inherit.aes = F, 
                 mapping=aes(x=t, y=nagents, fun.y="mean"), geom="line", color='darkgray')+ 
    scale_y_continuous(sec.axis = sec_axis(~.,name = "Number of agents per cluster (blue)", breaks = pretty_breaks(7)), 
                       breaks = pretty_breaks(7)) +
    theme(text = element_text(size = 14))
}



mean.cluster.size = function(df) {
  
  mc = cls.scatt.data(data=select(df, c( x, y)),
                      clust=as.integer(df$cluster + 1))
  mean.intracls.complete = mc %>% .$intracls.complete %>% mean
  #mean.intracls.single = mc %>% .$intracls.single %>% mean
  mean.intracls.average = mc %>% .$intracls.average %>% mean
  return(data.frame(mean.intracls.average, mean.intracls.complete))
}

create.cluster.metrics = function(flock) {
  nested = flock %>% filter(t >0 &  retry == 0) %>% 
    group_by(t) %>% nest()
  
  intracls = nested %>% mutate(data=map(.f = mean.cluster.size, .x=data)) %>%
    unnest(cols=c(data), .drop = T) %>% #select(-mean.intracls.single) %>%
    gather(2:3, key='intracls.measure', value='value') 
  return(intracls)
}


plot_ba_areas = function(flock) {
  number.clus.plot = flock %>% filter(retry==0) %>% plot_clusters() + labs(y="Number of clusters") +
    scale_x_continuous(breaks=pretty_breaks(10)) + xlim(0,250)  +
    scale_y_continuous(breaks=pretty_breaks(6))
  intracls = create.cluster.metrics(flock)   
  
  bars = flock %>% filter(retry==0) %>% 
    group_by(t) %>% 
    summarise(emergence = sum(behavior_type=='SC')) %>% transform(emergence = emergence > 50)
  
  retry_0_areas = data.frame(xmin=c(7,75,122,193), xmax=c(37,94,131,199), ymin=-Inf, ymax=Inf)
  
  intra.clus.plot = intracls %>%
    ggplot(data=., aes(x=t, y=value)) + 
    geom_point(aes(color=intracls.measure)) +
    theme(legend.position = "bottom", 
          text = element_text(size = 14)) +
    labs(y="Intra cluster measure", x="time(s)") + scale_x_continuous(breaks=pretty_breaks(10)) + xlim(0,250) +
    scale_y_continuous(breaks=pretty_breaks(6))
  
  bars_plot = geom_rect(inherit.aes = F, 
                        data=retry_0_areas, mapping = aes(xmin=xmin,xmax=xmax,ymax=ymax,ymin=ymin), alpha=0.3)

  birds.plot = flock %>% filter(retry==0 & t %in% c(1, 25, 75, 125, 250)) %>%
    ggplot(data=., aes(x=x, y=y, color=as.factor(cluster))) +
    geom_point() + facet_wrap(~ t, nrow = 1) + 
    theme(legend.position = 'none', axis.title = element_blank()) 
  
  g = ggarrange(number.clus.plot + bars_plot, intra.clus.plot + bars_plot, birds.plot, nrow = 3)
  return(g)
}

plot_vanilla_areas = function(flock) {
  number.clus.plot = flock %>% filter(retry==0) %>% plot_clusters() + labs(y="Number of clusters") +
    xlim(0,250)  + scale_x_continuous(breaks=pretty_breaks(15)) + 
    scale_y_continuous(breaks=pretty_breaks(6))
  intracls = create.cluster.metrics(flock)   
  
  intra.clus.plot = intracls %>%
    ggplot(data=., aes(x=t, y=value)) + 
    geom_point(aes(color=intracls.measure)) +
    theme(legend.position = "bottom", 
          text = element_text(size = 14)) +
    labs(y="Intra cluster measure", x="time(s)") +
    xlim(0,250) + scale_x_continuous(breaks=pretty_breaks(20)) + 
    scale_y_continuous(breaks=pretty_breaks(6))
  
  birds.plot = flock %>% filter(retry==0 & t %in% c(1, 85, 170, 250)) %>%
    ggplot(data=., aes(x=x, y=y, color=as.factor(cluster))) +
    geom_point() + facet_wrap(~ t, nrow = 1) + 
    theme(legend.position = 'none', axis.title = element_blank()) 
  
  g = ggarrange(number.clus.plot, intra.clus.plot, birds.plot, nrow = 3)
  return(g)
}

plot_fa_areas = function(flock) {
  number.clus.plot = flock %>% filter(retry==0) %>% plot_clusters() + labs(y="Number of clusters") +
    xlim(0,250)  + scale_x_continuous(breaks=pretty_breaks(15)) + 
    scale_y_continuous(breaks=pretty_breaks(6))
  intracls = create.cluster.metrics(flock)   
  
  bars = flock %>% filter(retry==0) %>% 
    group_by(t) %>% 
    summarise(emergence = sum(behavior_type=='AC')) %>% transform(emergence = emergence > 50) %>% filter(emergence == T)
  
  bars_plot = bars %>% geom_rect(data=., inherit.aes = F, 
                                     mapping=aes(xmin=t, xmax=t, ymin=-Inf, ymax=Inf), 
                                     color='black')
  
  intra.clus.plot = intracls %>%
    ggplot(data=., aes(x=t, y=value)) + 
    geom_point(aes(color=intracls.measure)) +
    theme(legend.position = "bottom", 
          text = element_text(size = 14)) +
    labs(y="Intra cluster measure", x="time(s)") +
    xlim(0,250) + scale_x_continuous(breaks=pretty_breaks(20)) + 
    scale_y_continuous(breaks=pretty_breaks(6))
  
  birds.plot = flock %>% filter(retry==0 & t %in% c(1, 87, 90, 250)) %>%
    ggplot(data=., aes(x=x, y=y, color=as.factor(cluster))) +
    geom_point() + facet_wrap(~ t, nrow = 1) + 
    theme(legend.position = 'none', axis.title = element_blank()) 
  
  g = ggarrange(number.clus.plot + bars_plot, intra.clus.plot + bars_plot, birds.plot, nrow = 3)
  return(g)
}


plot_clusters_agents(flocks.vanilla)
ggsave("~/proj/crazydevs/plots/flock_vanilla_clusters_agents.png", width = 12, height = 8)
plot_clusters_agents(flocks.ba)
ggsave("~/proj/crazydevs/plots/flock_ba_clusters_agents.png", width = 12, height = 8)
plot_clusters_agents(flocks.fa)
ggsave("~/proj/crazydevs/plots/flock_fa_clusters_agents.png", width = 12, height = 8)


plot_ba_areas(flocks.ba %>% drop_na)
ggsave("~/proj/crazydevs/plots/flock_ba_single_run_comparative.png", width = 12, height = 8)

plot_fa_areas(flocks.fa)
ggsave("~/proj/crazydevs/plots/flock_fa_single_run_comparative.png", width = 12, height = 8)

plot_vanilla_areas(flocks.vanilla)
ggsave("~/proj/crazydevs/plots/flock_vanilla_single_run_comparative.png", width = 12, height = 8)

