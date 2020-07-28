eb_f1 = read_file_from_experiment("/home/dfoguelman/proj/crazydevs/pythonpdevs/examples/mito/results10/xperiment_prob_fission_0.20_duration_1200.csv")
nl_f1 = read_csv("/home/dfoguelman/proj/crazydevs/pythonpdevs/examples/mito/results10/datos_netlogo_prob_0.2_duration_1200.csv")

eb_f2 = read_file_from_experiment("/home/dfoguelman/proj/crazydevs/pythonpdevs/examples/mito/results10/xperiment_prob_fission_0.50_duration_1200.csv")
nl_f2 = read_csv("/home/dfoguelman/proj/crazydevs/pythonpdevs/examples/mito/results10/datos_netlogo_prob_0.5_duration_1200.csv")

eb_f3 = read_file_from_experiment("/home/dfoguelman/proj/crazydevs/pythonpdevs/examples/mito/results10/xperiment_prob_fission_0.80_duration_1200.csv")
nl_f3 = read_csv("/home/dfoguelman/proj/crazydevs/pythonpdevs/examples/mito/results10/datos_netlogo_prob_0.8_duration_1200.csv")

nl = bind_rows(nl_f1, nl_f2, nl_f3)
eb = bind_rows(eb_f1, eb_f2, eb_f3)


eb %>% filter(state != "Inactive") %>% 
  add_column(mass_group=cut_width(.$mass, 1, boundary = 0)) %>% 
  group_by(currenttime, prob, mass_group) %>% 
  summarise(n=sum(mass)) %>%
  mutate(freq = n / sum(n), size=factor(mass_group, 
                                   labels=c("small", "medium", "large"))) %>%  
  ungroup() %>% add_column(simsource="ebdevs") %>%
  select(currenttime, size, freq, prob, simsource) %>% 
  rename(t=currenttime, percentage=freq) %>% 
  rbind(nl) %>% rename(fission_prob=prob) %>% 
  ggplot(data=., aes(x=t, y=percentage, color=simsource)) + geom_line() + 
   ylim(c(0, 1))+
  xlab("Time (s)") + ylab("Mass percentage")  +
  facet_grid(fission_prob ~ size, labeller = label_both)+
  
  theme(legend.position="top", 
        text = element_text(size=18), 
        strip.text = element_text(size=18), 
        axis.text = element_text(size=14),
        axis.title = element_text(size=18)) 
  
  
  
  eb %>% filter(state != "Inactive") %>% 
    add_column(mass_group=cut_width(.$mass, 1, boundary = 0)) %>% 
    group_by(currenttime, prob, mass_group) %>% 
    summarise(n=sum(mass)) %>%
    mutate(freq = n / sum(n), size=factor(mass_group, 
                                          labels=c("small", "medium", "large"))) %>%  
  ungroup() %>% add_column(simsource="ebdevs") %>%
    select(currenttime, size, freq, prob, simsource) %>% 
    rename(t=currenttime, percentage=freq) %>% 
    rbind(nl) %>%
  ggplot(data=., aes(x=t, y=percentage, color=size)) + geom_line() + facet_wrap(prob ~ simsource, nrow=3) + ylim(c(0, 1))
