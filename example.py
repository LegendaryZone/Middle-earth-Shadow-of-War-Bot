from main import API

a=API()
a.setVID('YOUR_ID_HERE')
a.setUUID('YOUR_ID_HERE')
a.UserAuth()
a.UserLoad()
a.Poll()
a.addItem(2584189485,4)#energy
a.addItem(2386669728,100000)#sc
a.addItem(2216831597,100000)#exp
a.addItem(1176006757,100000)#hc
#a.addItem(3414317992,1000)#vip token
#a.addItem(4220479132,0)#orc coins
#a.addItem(2778961937,900000)#power
#a.addItem(3709963089,0)#ability points
#a.addItem(4049818645,0)#glyp

a.injectStuff(531932187,4195647893,0,0,1,[2,3,4])
#a.UserSave(1648457619,531932187,4195647893,0,0,1,[2,3,4,5])
#a.UserSave(531932187,4111759798,2,0,1,[2,3,4,5],True)