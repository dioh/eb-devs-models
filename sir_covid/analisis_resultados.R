require(tidyverse)
require(rlang)
require(glue)

require(scales)

sir = read_csv("~/proj/crazydevs/pythonpdevs/examples/sir/results_no_emergence.csv",
               col_names = c('id','t','S','I','R','E','retry')) %>%
  add_column(Tot=.$S+.$I+.$R) 
sir$model='SIR-CM'

sir.emergent = read_csv("~/proj/crazydevs/pythonpdevs/examples/sir/results_emergence.csv", col_names = c('id','t','S','I','R','E','retry')) %>%
  add_column(Tot=.$S+.$I+.$R)
sir.emergent$model='SIR-CM-V'


sir.results = rbind(sir.emergent, sir)
  
# Remove short experiments
sir = sir %>% group_by(retry) %>% mutate(max_t = max(t)) %>% ungroup() %>% filter(max_t >= 400)
sir.emergent = sir.emergent %>% group_by(retry) %>% mutate(max_t = max(t)) %>% ungroup() %>% filter(max_t >= 400)


round.to.ten = function(x){
  small = (x %/% 10)  * 10
  large= small + 10
    if_else(x - small > large - x, large, small) %>% return
  }

filtro = data.frame(from=seq(0, 500, 10), to=seq(0, 500, 10)) %>% 
  glue_data("abs(t - {from}) == min(abs(t - {to}))") %>%
  glue_collapse(" | ")

sir.alineado = sir %>%
  group_by(retry) %>%
  filter(!! parse_quo(filtro, parent.frame())) %>%
  transform(t = round.to.ten(t))

sir.emergente.alineado = sir.emergent %>%
  group_by(retry) %>%
  filter(!! parse_quo(filtro, parent.frame())) %>%
  transform(t = round.to.ten(t))


sir %>%  filter(t != 'Inf') %>% add_column(tbin=cut_interval(.$t, 20)) %>% 
  gather("type", "amount", 3:5) %>%
  group_by(tbin, type) %>% 
  summarise(sum = sum(amount)) %>%
  add_column(dsum = c(.$sum[1], diff(.$sum))) %>%
  qplot(data=., x=tbin, y=dsum, color=type, facets = . ~ type)

sir %>%  filter(t != 'Inf') %>% 
  gather("type", "amount", 3:5) %>% add_column(tbin=cut_interval(.$t, 20)) %>%
  group_by(tbin, type) %>% mutate(mbin = mean(amount)) %>% 
  ggplot(data=., aes(x=tbin, y=amount, color=type)) + 
  facet_wrap(~ type, nrow=3) + 
  geom_boxplot() +
  stat_summary(fun.y=mean, geom="line", aes(group=1))  + 
  stat_summary(fun.y=mean, geom="point")
  
sir.results %>%  filter(t != 'Inf') %>% 
  gather("type", "amount", 3:5) %>% add_column(tbin=cut_interval(.$t, 20)) %>%
  ggplot(data=., aes(x=tbin, shape=model, y=amount, color=type)) + 
  facet_wrap(~ type, nrow=3) + 
  stat_summary(fun.y=mean, geom='point') +
  geom_smooth(method = 'loess')

sir.results %>%  filter(t != 'Inf') %>% 
  gather("type", "amount", 3:5) %>% #add_column(tbin=cut_interval(.$t, 20)) %>%
  ggplot(data=., aes(x=t, y=amount, color=paste(type, model))) + 
  facet_wrap(~ type, nrow=3) + 
  stat_summary(fun.y=mean, geom='point') +
geom_boxplot(outlier.shape = NA)

sires.alineados = sir.alineado %>% rbind(sir.emergente.alineado) 
sires.alineados %>% 
  gather("type", "amount", 3:5) %>% #add_column(tbin=cut_interval(.$t, 20)) %>%
  ggplot(data=., aes(x=t, y=amount, shape=model,
                     color=paste(type, model))) + 
  facet_wrap(~ type, nrow=3) +
    scale_x_continuous(breaks = pretty_breaks(10)) +
  stat_summary(fun.y=mean, geom='point', size=3) +
  stat_summary(fun.y=mean, geom='line') +
  # stat_boxplot(position="stack")
  stat_summary(fun.y = mean,
               fun.ymin = function(x) mean(x) - sd(x),
               fun.ymax = function(x) mean(x) + sd(x),
               geom = "errorbar", alpha=0.5) 
+
geom_vline(xintercept = (sires.alineados %>% filter(retry==10 & E==T) %>% select(t))$t)  

+ #, color='gray')
  geom_col(inherit.aes = F,aes(x=t, y=E))
  geom_vline(xintercept = (sires.alineados %>% filter(E==T) %>% select(t))$t)  
  
geom_col(inherit.aes=F, 
             data=filter(sires.alineados, E > 50),
           mapping = aes(x=t, y=1))

sir %>% 
    gather("type", "amount", 3:5) %>%
    qplot(data=., x=t, y=amount, color=type) + 
    stat_summary(fun.y=mean, geom="line", aes(group=1))  + 
    stat_summary(fun.y=mean, geom="point")
  
