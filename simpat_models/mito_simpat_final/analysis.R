require(tidyverse)
require(gganimate)
require(ggforce)
require(scales)
require(igraph)

dir = "/home/danito/proj/crazydevs/pythonpdevs/examples/mito/results8"
setwd(dir)
files = dir(dir, pattern="*.csv")

read_file_from_experiment = function(x) read_csv(file = x, col_types = cols(child = col_number(),
                                    fusionatedwith = col_number(), oldmass = col_double(), 
                                    parent = col_number())) %>% add_column(.data = ., prob= str_extract(x, "[0-9].[0-9]"))

data <- files %>%
  map(read_file_from_experiment) %>%
                       # read in all the files individually, using
                       # the function read_csv() from the readr package
  reduce(bind_rows)        # reduce with rbind into one dataframe
data


data %>% filter(state != "Inactive") %>% group_by(currenttime, prob) %>%  rename(fission_prob=prob) %>%
  summarise(totmass = sum(mass)) %>% 
  qplot(data=., x=currenttime, y=round(totmass, digits = 8)) +
   facet_grid(fission_prob ~ ., labeller = label_both)+
  scale_x_continuous(breaks = pretty_breaks(20)) + 
    xlab("Time (s)") + ylab("Total Mass")  +
  theme(legend.position="top", 
        text = element_text(size=18), 
        strip.text = element_text(size=18), 
        axis.text = element_text(size=14),
        axis.title = element_text(size=18)) 


mito = read_csv('~/proj/crazydevs/pythonpdevs/examples/mito/out',
                col_types = cols(oldmass = col_double(), parent = col_double()))

mito %>% filter(currenttime == 0 & state != 'Inactive') %>%
  qplot(data=., x=position_x, y=position_y, color=area)


f1 = read_file_from_experiment("/home/danito/proj/crazydevs/pythonpdevs/examples/mito/results8/xperiment_prob_fission_0.20.csv")
f2 = read_file_from_experiment("/home/danito/proj/crazydevs/pythonpdevs/examples/mito/results8/xperiment_prob_fission_0.50.csv")
f3 = read_file_from_experiment("/home/danito/proj/crazydevs/pythonpdevs/examples/mito/results8/xperiment_prob_fission_0.80.csv")

data = bind_rows(f1, f2, f3)

nlogo = read_csv("/home/dfoguelman/proj/crazydevs/pythonpdevs/examples/mito/results10/datos_netlogo_prob_0.2_duration_1200.csv")

mit050 %>% filter(state != "Inactive") %>% group_by(currenttime) %>% 
  summarise(totmass = sum(mass)) %>% 
  qplot(data=., x=currenttime, y=round(totmass, digits = 8)) + 
scale_x_continuous(breaks = pretty_breaks(10)) 



##### Animation
mito %>% #filter(state=="Inactive") %>% 
  ggplot(data=.,
                aes(x=position_x, y=position_y, color=area)) +
  geom_point() + 
  transition_manual(currenttime) +  
  labs(title = 'Time: {frame} of {nframes}')


animaton = mit050 %>% filter(state != "Inactive") %>%  
  ggplot(data=.,
         aes(x=position_x, 
             y=position_y, 
             color=area, size=mass)) + theme_minimal() +
  geom_point() + transition_manual(currenttime) +
  geom_point(data=filter(mit050, id==10 & state != "Inactive"),
             color="black", aes(shape=as.factor(area), size=mass)) + 
  geom_circle(aes(x0=x0, y0=y0, r=r), inherit.aes = F, data=circles)

animate(animaton, height = 800, width =800)


# Plot of mitos


# Mitos dradius parameters

circles <- data.frame(
  x0 = rep(0, 3),
  y0 =  rep(0, 3),
  r =     c(50.0/2, 16.6/2, 25.0/2)
)
ggplot() + geom_circle(aes(x0=x0, y0=y0, r=r), data=circles)

plot = mito %>% filter(state != "Inactive" & (currenttime %% 50 == 0 )) %>%  
  ggplot(data=.,
         aes(x=position_x, 
             y=position_y, 
             color=area)) +
  geom_point() + #facet_wrap(. ~ currenttime) + 
  geom_point(data=filter(mito, id==10 & state != "Inactive"
                         & currenttime %% 50 == 0 ), color="black", aes(shape=as.factor(area)), size=3) + 
  geom_circle(aes(x0=x0, y0=y0, r=r), inherit.aes = F, data=circles)

# Plot the partial masses

eb %>% filter(state != "Inactive") %>% 
  add_column(mass_group=cut_width(.$mass, 1, boundary = 0)) %>% 
  group_by(currenttime, fissionprob, mass_group) %>% summarise(n=n()) %>% mutate(freq = n / sum(n)) %>% 
  ggplot(data=., aes(x=currenttime, y=freq, color=factor(mass_group, 
                                                         labels=c("Small", "Medium", "Large")))) + 
  facet_grid(fissionprob ~ ., labeller = label_both) +
  geom_line() +
  scale_colour_manual(values = c("yellow", "blue", "green"))
  scale_y_continuous(breaks = pretty_breaks(8)) + ylim(limits=c(0, 1)) +
  scale_x_continuous(breaks = pretty_breaks(20)) + 
  labs(x="Time (s)", y="Percentage of Mitos by size", color="Mass group")  +
  theme(legend.position="top", 
        text = element_text(size=18), 
        strip.text = element_text(size=18), 
        axis.text = element_text(size=14),
        axis.title = element_text(size=18)) 

mito05 %>% filter(state != "Inactive") %>% group_by(currenttime) %>% 
  summarise(totmass = sum(mass)) %>% 
  qplot(data=., x=currenttime, y=round(totmass, digits = 8)) + scale_x_continuous(breaks = pretty_breaks(10)) 

mito %>% filter(currenttime >= 300) %>%
  select(currenttime, id, name, mass, oldmass, parent, ta, state, fusionatedwith) %>%
  arrange(currenttime, id) %>% View


# Graphg analisis interacciones
t = 30
fusion.graph = mit050 %>%
  filter(currenttime == t & !is.na(fusionatedwith)) %>%
  select(id, fusionatedwith) %>% rename(id2=fusionatedwith) %>%
  add_column(tipo="fusion")

fission.graph = mit050 %>% filter(currenttime == t & !is.na(parent)) %>%
  select(id, parent) %>% add_column(tipo="fission") %>% rename(id2=parent)

g90 = rbind(fusion.graph, fission.graph)
g60 = rbind(fusion.graph, fission.graph)
g30 = rbind(fusion.graph, fission.graph)


grafo = rbind(fusion.graph, fission.graph) %>% igraph::graph_from_data_frame(.)

grafo = difference(g90%>% igraph::graph_from_data_frame(.), g60 %>% igraph::graph_from_data_frame(.))

E(grafo)$color <- as.factor(E(grafo)$tipo)
l = igraph::layout_as_tree(grafo, mode = "out")
plot(grafo, vertex.color="lightsteelblue", vertex.frame.color="white",
     vertex.name=NULL, vertex.size=3, vertex.shape="circle", 
     edge.color=grafo$tipo, edge.width=1, vertex.label=NA,
     edge.arrow.size=0.1, edge.curved=0.1, layout=l)


######### Multiple retry plot on sqlite

con <- DBI::dbConnect(
  RSQLite::SQLite( syncronous=NULL),
  dbname = "/home/dfoguelman/proj/crazydevs/pythonpdevs/examples/mito/mito_experiment.sqlite")

data = tbl(con, "mitostate") %>% select(id, currenttime, mass, fissionprob, state, retry) %>%
  filter(duration == 3600)

eb = data %>% as_tibble() 

eb2 = eb %>% filter(state!="Inactive") %>%
  add_column(mass_group=factor(cut_width(.$mass, 1, boundary = 0),
                               labels=c("small", "medium", "large"))) %>%
  group_by(currenttime, retry, fissionprob, mass_group) %>%
  summarise(group_mass=sum(mass)) %>%
  mutate(freq = group_mass / sum(group_mass),
         tot=sum(group_mass), fission_prob=factor(fissionprob, levels=c(0.8, 0.5, 0.2))) %>%
  ungroup() %>% add_column(simsource="ebdevs")

eb2 %>% filter(state != "Inactive") %>% 
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
  facet_grid(fission_prob ~ size, labeller = label_both) +
  theme(legend.position="top", 
        text = element_text(size=18), 
        strip.text = element_text(size=18), 
        axis.text = element_text(size=14),
        axis.title = element_text(size=18))


eb = read_csv("/home/dfoguelman/proj/crazydevs/pythonpdevs/examples/mito/experimento_duration_3600.csv")

eb %>% ggplot(data=., aes(x=currenttime, y=perc, color=mass_group)) + geom_line() + 
  ylim(c(0, 1))+
  xlab("Time (s)") + ylab("Mass percentage")  +
  facet_wrap(~ fissionprob) +
  theme(legend.position="top", 
        text = element_text(size=18), 
        strip.text = element_text(size=18), 
        axis.text = element_text(size=14),
        axis.title = element_text(size=18))

eb = read_csv("/home/danito/proj/crazydevs/pythonpdevs/examples/mito/results/experimento_3600.csv", 
              col_names = c("currenttime","fissionprob","state","retry","perc","mass_group"),
              col_types = cols(currenttime = col_number(),
                               fissionprob = col_number(), state = col_character(), retry = col_number(), 
                               perc=col_double(), 
                               mass_group = col_character()))

eb %>% filter(retry==1) %>% ggplot(data=., aes(x=currenttime, y=perc)) +
  stat_summary(aes(y=perc, group=mass_group),
               inherit.aes = T,
               fun.data=mean_se,
               alpha=0.1,
               geom='crossbar',
               color="gray") +
  facet_grid( fissionprob ~ mass_group, labeller = label_both) +
  stat_summary(aes(y=perc, color=mass_group),
               fun.y =mean, fun.args = list(mult=1), geom='line') +
  scale_colour_manual(values = c("#d69c30", "#44648a", "#50863b")) +
  scale_y_continuous(breaks = pretty_breaks(10)) +
  ylim(limits=c(0, 1)) +
  scale_x_continuous(breaks = pretty_breaks(10)) + 
  labs(x="Time (s)", y="Percentage of Mitos by size", color="Mass group", linetype = "Model version")  +
  theme(legend.position="top", 
        text = element_text(size=18), 
        strip.text = element_text(size=18), 
        axis.text = element_text(size=14),
        axis.text.x = element_text(angle=45),
        axis.title = element_text(size=18)) +
  geom_line(data=netlogo.data, inherit.aes = F,
             mapping = aes(x=currenttime, y=perc, color=mass_group),
            linetype=2)


files = dir("~/proj/crazydevs/pythonpdevs/examples/mito/results_nlogo/modified_model/", 
            pattern="*.csv",
            include.dirs = T, full.names = T)

netlogo.data <- files %>%
  map(read_csv) %>%
  reduce(bind_rows)        # reduce with rbind into one dataframe
netlogo.data


geom_point(data=netlogo.data, inherit.aes = F, mapping = aes(x=currenttime, y=perc, color=mass_group))



### Ploting events

nlogo_events = read_csv("~/proj/crazydevs/code_paper_orig amount of mitos fusion fission both none.csv")
eb_events = read_csv("~/proj/crazydevs/pythonpdevs/examples/mito/results/fusion_fission_amount.csv", 
                     col_names = c("currenttime", "prob", "amount", "dration", "type", "retry"))

qplot(data=nlogo_events, x=currenttime, y=amount, color=type, geom='line')

eb_events %>% filter(type =="Fusionated") %>% arrange(currenttime, prob, type) %>% qplot(data=., x=currenttime, fill=retry)
eb_events %>% filter(type =="Fusionated") %>% qplot(data=., x=currenttime, fill=retry)
eb_events %>% ggplot(data=., aes(x=currenttime, y=amount)) + stat_summary()
eb_events %>% ggplot(data=., aes(x=currenttime, y=amount, color=type)) + stat_summary()
eb_events %>% ggplot(data=., aes(x=currenttime, y=amount, color=type)) + stat_summary(mapping = aes(group=type))
eb_events %>% ggplot(data=., aes(x=currenttime, y=amount, color=type)) + stat_summary(mapping = aes(group=type)) + facet_wrap( . ~ prob)
eb_events %>% ggplot(data=., aes(x=currenttime, y=amount, color=type)) + stat_summary(mapping = aes(group=type)) + facet_wrap( . ~ prob, nrow=3)

eb_events %>% filter(prob==0.5) %>% ggplot(data=., aes(x=currenttime, y=amount,
                                                       color=type, geom='line')) +
  stat_summary(mapping = aes(group=type))
