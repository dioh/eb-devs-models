require(tidyverse)
require(scales)

model.eb = read_csv("/home/dfoguelman/proj/crazydevs/pythonpdevs/examples/mito/results/experiment_3600duration_20_retrues.csv", 
              col_names = c("currenttime","fissionprob","state","retry","perc","mass_group", 'duration'),
              col_types = cols(currenttime = col_number(),
                               fissionprob = col_number(), state = col_character(), retry = col_number(), 
                               perc=col_double(), 
                               mass_group = col_character(), duration=col_number())) %>% transform(retry=retry-19) %>%
  rename(t=currenttime) %>% select(-c(state, duration)) %>% add_column(model='EB-DEVS')

model.nl = read_csv("/home/dfoguelman/proj/crazydevs/pythonpdevs/examples/mito/results/netlogo_results.csv",
                    col_types = cols(large=col_double(), 
                                     medium=col_double(),
                                     small=col_double(),
                                     retry=col_number(),
                                     fission_prob=col_double(),
                                     t=col_number())) %>% 
  add_column(model='Netlogo') %>%
  rename(fissionprob=fission_prob) %>%
  gather(1:3, key = "mass_group", value = "perc")




model.nl %>% rbind(model.eb) %>% #filter(t<6000) %>% 
  group_by(model, mass_group, fissionprob, t) %>% summarise(mperc = mean(perc), sperc=sd(perc)) %>% #View()
  ggplot(data=.,
         aes(x=t)) +
  geom_crossbar(aes(y = mperc, ymin = mperc -sperc, ymax=mperc+sperc), alpha=0.9, color='gray') +
  geom_point(aes(y=mperc, color=model)) + 
  facet_grid(  mass_group ~ fissionprob, labeller = function(x) label_both(str_remove)) 

  facet_grid(  ~ fissionprob, labeller = label_both) +
  stat_summary(aes(y=perc, color=model, group =mass_group),
               fun.y =mean, fun.args = list(mult=1), geom='line') 


model.nl %>% rbind(model.eb) %>% 
  ggplot(data=.,
         aes(x=t, y=perc)) +
  facet_grid( mass_group ~ fissionprob, labeller = label_both, scale='free') +
stat_summary(aes(y=perc, group=model),
             inherit.aes = T,
             fun.data=mean_se,
             alpha=0.1,
             geom='crossbar',
             color="gray") +
  stat_summary(aes(y=perc, color=model, group =model),
               fun.y =mean,  geom='line') + 
    scale_colour_manual(values = c("#d69c30", "#44648a", "#50863b")) +
  scale_y_continuous(breaks = pretty_breaks(10)) +
  ylim(limits=c(0, 1)) +
  scale_x_continuous(breaks = pretty_breaks(10)) + 
  labs(x="Time (s)", y="Percentage of Mitos by size", color="Mass group", linetype = "Model version")  +
  # theme_light() +
  theme(legend.position="top", 
        text = element_text(size=14), 
        strip.text = element_text(size=14), 
        axis.text = element_text(size=14),
        axis.text.x = element_text(hjust = 1, angle=45),
        axis.title = element_text(size=14))

ggsave("~/proj/crazydevs/plots/results_mito_ebdevs_vs_nlogo.png", width = 12, height = 8)

# Three subplots one by fission prob


model.nl %>% rbind(model.eb) %>%
  transform(mass_group = str_to_title(mass_group)) %>%
  filter(t %% 10 ==0) %>%
  unite(model_by_group, c(mass_group, model), sep=' ') %>% 
  ggplot(data=.,
         aes(x=t, y=perc)) +
  facet_grid( fissionprob ~ .,
               labeller = label_both, scale='free') +
  # facet_wrap( ~ fissionprob, nrow=3, scale="free") +
  stat_summary(aes(y=perc, group=model_by_group),
               inherit.aes = T,
               fun.data=mean_se,
               alpha=0.1,
               geom='crossbar',
               color="gray") +
  stat_summary(aes(y=perc, color=model_by_group,
                   group =model_by_group),
               fun.y =mean,  geom='line') + 
  scale_colour_manual(values = c('#805d1d', "#d69c30",  "#44648a",'#73a9ea', "#50863b", '#7acd5a')) +
  scale_y_continuous(breaks = pretty_breaks(5)) +
  scale_x_continuous(breaks = pretty_breaks(10)) + 
  labs(x="time (s)", y="Percentage of Mitos by size", color="Mass group by model", linetype = "Model version")  +
  theme(legend.position="top", 
        text = element_text(size=14), 
        strip.text = element_text(size=14), 
        axis.text = element_text(size=14),
        axis.text.x = element_text(hjust = 1, angle=45),
        axis.title = element_text(size=14))

ggsave("~/proj/crazydevs/plots/results_mito_ebdevs_vs_nlogo_three_subplots.png", width = 12, height = 8)


# Error analysis
inner_join(model.nl, model.eb,
           by=c("t", "retry", "fissionprob", 'mass_group'),
           suffix = c('.nl', '.eb')) %>%
  group_by(fissionprob, mass_group) %>%
  summarise(RMSE = sqrt(mean(perc.nl - perc.eb)**2)) %>%
  ggplot(data=., aes(x=mass_group, y=RMSE, fill=as.factor(fissionprob))) +
  geom_col(position = position_dodge2()) +
  scale_x_discrete(limits=c('small', 'medium', 'large')) + 
  labs(x="Mass group", y="RMSE", fill="Fission probability")  + 
  # theme_light() +
  theme(legend.position="top", 
        text = element_text(size=14), 
        strip.text = element_text(size=14), 
        axis.text = element_text(size=14),
        axis.text.x = element_text(hjust = 0.5),
        axis.title = element_text(size=14))
  
ggsave("~/proj/crazydevs/plots/results_mito_ebdevs_vs_nlogo_RMSE.png", width = 12, height = 8)


# Error analysis
inner_join(model.nl, model.eb,
           by=c("t", "retry", "fissionprob", 'mass_group'),
           suffix = c('.nl', '.eb')) %>%
  group_by(fissionprob, mass_group) %>%
  summarise(RMSE = sqrt(mean(perc.nl - perc.eb)**2)) %>%
  ggplot(data=., aes(x=t, y=RMSE, color=mass_group)) +
  facet_wrap(mass_group ~ fissionprob, nrow = 3) +
  geom_point() +
  labs(x="Mass group", y="RMSE", color="Fission probability")  + 
  # theme_light() +
  theme(legend.position="none", 
        text = element_text(size=14), 
        strip.text = element_text(size=14), 
        axis.text = element_text(size=14),
        # axis.text.x = element_text(hjust = 0.5),
        axis.title = element_text(size=14))

ggsave("~/proj/crazydevs/plots/results_mito_ebdevs_vs_nlogo_RMSE.png", width = 12, height = 8)

# Corr analysis
vars_keep <- names(both.models)[c(4,7)]
some <- both.models %>% split(.$fissionprob) %>% map(select, vars_keep) %>% map(cor)


## Counting the amount of events

fisions = read_csv("~/proj/crazydevs/pythonpdevs/examples/mito/results_events_all_3.csv")

fisions %>% filter(currenttime %% 300 == 0) %>% group_by(fissionprob, currenttime, retry)  %>% 
  mutate(tot = sum(`count(1)`), perc=`count(1)` / tot) %>% ungroup %>%  
  filter(requestedstate %in% c('Fusionated', 'Fissionated')) %>%
  # group_by(fissionprob, currenttime)  %>% View
  ggplot(data=., aes(x=currenttime, y=perc)) + 
  stat_summary(aes( y=perc, group=requestedstate, color=requestedstate),
               inherit.aes = T,
               fun.y=mean,
               geom='point') + 
  stat_summary(aes( y=perc, group=requestedstate, color=requestedstate),
               inherit.aes = T,
               fun.data=mean_se,
               geom='crossbar') +
  facet_wrap(~ fissionprob)
         

fisions %>% filter(requestedstate %in% c('Fusionated', 'Fissionated')) %>% 
  group_by(fissionprob, currenttime)  %>% 
  qplot(data=., x=requestedstate, y=`count(1)`,
        color=requestedstate, geom='violin') + 
  labs(y='AMount of events;') + 
  scale_x_continuous(breaks = pretty_breaks(10)) + 
  facet_wrap( ~ fissionprob, scale='free')
