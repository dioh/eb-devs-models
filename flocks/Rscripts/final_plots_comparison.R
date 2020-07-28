require(tidyverse)
require(scales)

model.eb.d1 = read_csv("/home/dfoguelman/proj/crazydevs/pythonpdevs/examples/mito/experiment_cicles_12_retries_20_duration_d1.csv",
                    col_names = c("currenttime","fissionprob","state","retry","perc","mass_group", 'duration'),
                    col_types = cols(currenttime = col_number(),
                                     fissionprob = col_number(),
                                     state = col_character(),
                                     retry = col_number(), 
                                     perc=col_double(), 
                                     mass_group = col_character(), 
                                     duration=col_number())) %>% transform() %>%
  rename(t=currenttime) %>% select(-c(state, duration)) %>% add_column(model='EB-DEVS-d1', duration=3600)


model.eb.dr1 = read_csv("/home/dfoguelman/proj/crazydevs/pythonpdevs/examples/mito/experiment_cicles_12_retries_10_duration_dradius.csv",
                       col_names = c("currenttime","fissionprob","state","retry","perc","mass_group", 'duration'),
                       col_types = cols(currenttime = col_number(),
                                        fissionprob = col_number(),
                                        state = col_character(),
                                        retry = col_number(), 
                                        perc=col_double(), 
                                        mass_group = col_character(), 
                                        duration=col_number())) %>% transform() %>%
  rename(t=currenttime) %>% select(-c(state, duration)) %>% add_column(model='EB-DEVS-dradius', duration=3600)

model.nl.orig = read_csv("/home/dfoguelman/proj/crazydevs/results/netlogo_results_fuse_all.csv",
                        col_types = cols(large=col_double(), 
                                         medium=col_double(),
                                         small=col_double(),
                                         retry=col_number(),
                                         fission_prob=col_double(),
                                         t=col_number())) %>% 
  add_column(model='NetlogoOrig') %>%
  rename(fissionprob=fission_prob) %>%
  gather(1:3, key = "mass_group", value = "perc") %>% select(-contains("_event")) 

model.nl.modif = read_csv("/home/dfoguelman/proj/crazydevs/results/netlogo_results_fuse_model_prueba2.csv",
                         col_types = cols(large=col_double(), 
                                          medium=col_double(),
                                          small=col_double(),
                                          retry=col_number(),
                                          fission_prob=col_double(),
                                          t=col_number())) %>% 
  add_column(model='NetlogoModif') %>%
  rename(fissionprob=fission_prob) %>%
  gather(1:3, key = "mass_group", value = "perc") %>% select(-contains("_event")) 




bind_rows(list(model.eb.dr1, model.nl.modif, model.nl.orig)) %>%
  filter(fissionprob >=0.2 & fissionprob<=0.8) %>%

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
  # scale_colour_manual(values = c("#d69c30", "#44648a", "#50863b")) +
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


bind_rows(list( model.eb.dr1, model.nl.modif)) %>%
  filter(fissionprob >=0.2 & fissionprob<=0.8) %>%
  
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
  # scale_colour_manual(values = c("#d69c30", "#44648a", "#50863b")) +
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



vs.modif.rmse = inner_join(model.nl.modif, model.eb.dr1,
           by=c("t", "retry", "fissionprob", 'mass_group'),
           suffix = c('.nl', '.eb')) %>%
  group_by(fissionprob, t) %>%
  summarise(RMSE = sqrt(mean(perc.nl - perc.eb)**2)) %>% add_column(vs='EB-DEVS vs NetLogo modified model')


vs.orig.rmse = inner_join(model.nl.orig, model.eb.dr1,
           by=c("t", "retry", "fissionprob", 'mass_group'),
           suffix = c('.nl', '.eb')) %>%
  group_by(fissionprob, t) %>%
  summarise(RMSE = sqrt(mean(perc.nl - perc.eb)**2))%>% add_column(vs='EB-DEVS vs NetLogo original model')


rbind(vs.orig.rmse, vs.modif.rmse) %>%
  ggplot(data=., aes(x=t, y=RMSE, color=vs)) +
  facet_grid(fissionprob ~ ., labeller = label_context) +
  geom_point(size=0.3) +
  labs(x="Time(s)", y="RMSE", color="")  + 
  # theme_light() +
  theme(legend.position="top", 
        text = element_text(size=14), 
        strip.text = element_text(size=14), 
        axis.text = element_text(size=14),
        # axis.text.x = element_text(hjust = 0.5),
        axis.title = element_text(size=14))
