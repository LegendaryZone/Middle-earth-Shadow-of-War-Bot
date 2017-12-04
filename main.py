# -*- coding: utf-8 -*-
import requests
import json
import time
import random
import sys
import base64

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class API(object):
	def __init__(self):
		self.debug=True
		self.s=requests.session()
		self.s.headers.update({'User-Agent':'Mesh/1.2.42443-1.4.1 (iOS; 10.2)','Content-Type':'application/json'})
		self.s.verify=False
		self.base_auth={'Authorization':'Basic bGV2aWF0aGFuOnZXOG11Yld6YXMybkZ2WkpwcUJ6TG1na0tUdjdOVk0yYXJQOE5XamU='}
		self.s.headers.update(self.base_auth)
		self.AssetsBranchId=10401
		self.last_error=None
		self.user={}
		self.user_data={}
		self.add={}
		self.hard_coded_add=255
		self.AppUUID=self.genRandomDeviceID()
		self.more=False

	def setInjectMore(self):
		self.more=True

	def updateAuth(self,user_id,password):
		self.base_auth={'Authorization':'Basic %s'%(base64.b64encode('%s:%s'%(user_id,password)))}
		self.s.headers.update(self.base_auth)
		
	def getLastError(self):
		return self.last_error

	def setLastError(self,id):
		self.last_error=id
		
	def setVID(self,id):
		self.log('device_id:%s'%(id))
		self.VID=id
		
	def setADID(self,id):
		self.ADID=id

	def log(self,msg):
		if self.debug:
			print '[%s]: %s'%(time.strftime('%H:%M:%S'),msg)

	def gRH(self,n):
		return ''.join([random.choice('0123456789ABCDEF') for x in range(n)])
		
	def genRandomDeviceID(self):
		return '%s-%s-%s-%s-%s'%(self.gRH(8),self.gRH(4),self.gRH(4),self.gRH(4),self.gRH(12))

	def callAPI(self,url,data):
		r=self.s.post('https://game.sow.iugome.com/v1/'+url,data=json.dumps(data))
		if 'error' in r.content and 'message' in r.content:
			self.setLastError(json.loads(r.content)['message'])
			print self.getLastError()
			return None
		else:
			return json.loads(r.content)

	def UserAuth(self):
		data={}
		data['AssetsBranchId']=self.AssetsBranchId
		data['AppUUID']=self.AppUUID
		data['UUIDs']=[]
		data['CrashId']=''
		data['CrashKey']=''
		data['CrashTimestamp']=0
		data['IsTest']=0
		data['VID']=self.VID
		data['ADID']='00000000-0000-0000-0000-000000000000' if not hasattr(self,'ADID') else self.ADID
		data['DeviceName']='iPad5,4'
		data['DeviceModel']='iPad'
		data['GpuVendor']="Apple Inc."
		data['GpuModel']="Apple A8X GPU"
		data['GpuVersion']="OpenGL ES 2.0 Apple A8X GPU - 95.55"
		data['MemoryTotalSize']=1869594624
		data['ScreenPPI']=2.639999866e2
		data['ScreenResolution']=[1536, 2048]
		data['Locale']='en_DE'
		data['Country']='DE'
		data['Language']="en-GB"
		data['TimeFromGMT']=32400
		data['ConnectionType']='WiFi'
		data['SizeOfFiles']=131109684
		data['SizeOfDocuments']=1410
		data['SizeOfCache']=4096
		data['SizeOfLibrary']=2850292
		res=self.callAPI('UserAuth',data)
		if not res:
			self.log('dont have data')
			return
		self.user=res
		self.log('our UserId:%s RealmId:%s Password:%s FriendCode:%s'%(self.user['UserId'],self.user['RealmId'],self.user['Password'],self.user['FriendCode']))
		self.updateAuth(self.user['UserId'],self.user['Password'])
		return res
		
	def UserLoad(self):
		data={}
		data['DataVersion']=self.AssetsBranchId
		res= self.callAPI('UserLoad',data)
		if not res:
			self.log('UserLoad failed')
			return
		self.user_data=res['Data']
		return res
		
	def NewsFetch(self):
		data={}
		data['Version']=2
		data['RealmId']=self.user['RealmId']
		data['GuildId']=0
		data['Id']=0
		data['Lang']='en-GB'
		data['Recover']=[]
		return self.callAPI('NewsFetch',data)
		
	def Poll(self):
		data={}
		data['Timestamp']=int(time.time())
		data['AssetsBranchId']=self.AssetsBranchId
		data['RealmId']=self.user['RealmId']
		data['GuildId']=0
		data['IsActive']=1
		data['PerformanceTier']=0
		data['DisplayScale']=1
		data['Fps']=59
		data['FpsMin']=35
		data['FpsMax']=60
		data['FpsMean']=5.658823490e1
		data['FpsVariance']=3.835986614e1
		res= self.callAPI('Poll',data)
		self.AssetsVersion=res['AssetsVersion']
		self.OverlayVersion=res['OverlayVersion']
		return res

	def createVerifier(self,Region,Quest,StageIndex,Difficulty,TimesSimmed,Team,InitialCredits):
		data={}
		data['Region']=Region
		data['Quest']=Quest
		data['StageIndex']=StageIndex
		data['Difficulty']=Difficulty
		data['TimesSimmed']=TimesSimmed
		data['Team']=Team
		data['InitialCredits']=InitialCredits
		return json.dumps(data).replace(' ','')

	def addItem(self,id,num):
		self.add[id]=num

	def getNumAdd(self,id,bad=False):
		if not bad:
			if id in self.add:
				return self.add[id]
		return 0
		
	def addNewTransactions(self,_Type,DataTimestamp,Timestamp,items=False):
		data={}
		data['Type']=_Type
		data['Debit']=[]
		data['Credit']=[]
		data['Debit'].append({'Type':2468616184,'Item':2584189485,'Amount':self.getNumAdd(2584189485)})#no energy use
		data['Credit'].append({'Type':2468616184,'Item':2584189485,'Amount':self.getNumAdd(2584189485,True)})#no energy gain			
		if items:
			if 'Glyphs' in self.user_data and self.more:
				for i in self.user_data['Glyphs']['List']:
					data['Credit'].append({'Type':1594795060,'Item':i['Item'],'Amount':self.hard_coded_add})
			if 'Inscriptions' in self.user_data and self.more:
				for i in self.user_data['Inscriptions']['List']:
					data['Credit'].append({'Type':2576699940,'Item':i['Item'],'Amount':self.hard_coded_add})
			if 'InscriptionFragments' in self.user_data and self.more:
				for i in self.user_data['InscriptionFragments']['List']:
					data['Credit'].append({'Type':1320415692,'Item':i['Item'],'Amount':self.hard_coded_add})
			if 'RuneFragments' in self.user_data and self.more:
				for i in self.user_data['RuneFragments']['List']:
					data['Credit'].append({'Type':1169956836,'Item':i['Item'],'Amount':self.hard_coded_add})
			if 'XPPotions' in self.user_data and self.more:
				for i in self.user_data['XPPotions']['List']:
					data['Credit'].append({'Type':423610028,'Item':i['Item'],'Amount':self.hard_coded_add})
			data['Credit'].append({'Type':2468616184,'Item':1217894615,'Amount':self.getNumAdd(1217894615)})#hero exp
			data['Credit'].append({'Type':2468616184,'Item':2216831597,'Amount':self.getNumAdd(2216831597)})#exp
			data['Credit'].append({'Type':2468616184,'Item':2386669728,'Amount':self.getNumAdd(2386669728)})#soft currency
			data['Credit'].append({'Type':2468616184,'Item':1176006757,'Amount':self.getNumAdd(1176006757)})#hard currency
			data['Credit'].append({'Type':2468616184,'Item':3414317992,'Amount':self.getNumAdd(3414317992)})#vip token
			data['Credit'].append({'Type':2468616184,'Item':4220479132,'Amount':self.getNumAdd(4220479132)})#orc coin
			data['Credit'].append({'Type':2468616184,'Item':3709963089,'Amount':self.getNumAdd(3709963089)})#ability points
			data['Credit'].append({'Type':2468616184,'Item':2778961937,'Amount':self.getNumAdd(2778961937)})#power
			data['Credit'].append({'Type':2468616184,'Item':453716564,'Amount':self.getNumAdd(453716564)})#black gemstone
			#data['Verifier']=self.createVerifier(Region,Quest,StageIndex,Difficulty,TimesSimmed,Team,data['Credit'])
		data['Data']=None
		data['AssetsBranchId']=self.AssetsBranchId
		data['AssetsVersion']=self.AssetsVersion
		data['OverlayComplete']=1
		data['OverlayVersion']=self.OverlayVersion
		data['DataTimestamp']=DataTimestamp
		data['Timestamp']=Timestamp
		return data

	def addGlyph(self,data):
		tmp=data
		for idx, i in enumerate(data['List']):
			if i['Item'] in self.add:
				tmp['List'][idx]['Amount']+=self.getNumAdd(i['Item'])
		return tmp

	def addHardCoded(self,data):
		tmp=data
		for idx, i in enumerate(data['List']):
			tmp['List'][idx]['Amount']+=self.hard_coded_add
		return tmp

	def UserSave(self,fin_data):
		data={}
		tmp={}
		tmp['GlobalSecurity']=self.user_data['GlobalSecurity']
		tmp['Security']=self.user_data['Security']
		if 'Glyphs' in self.user_data:
			tmp['Glyphs']=self.addHardCoded(self.user_data['Glyphs'])
		if 'Inscriptions' in self.user_data:
			tmp['Inscriptions']=self.addHardCoded(self.user_data['Inscriptions'])
		if 'InscriptionFragments' in self.user_data:
			tmp['InscriptionFragments']=self.addHardCoded(self.user_data['InscriptionFragments'])
		if 'RuneFragments' in self.user_data:
			tmp['RuneFragments']=self.addHardCoded(self.user_data['RuneFragments'])
		if 'XPPotions' in self.user_data:
			tmp['XPPotions']=self.addHardCoded(self.user_data['XPPotions'])
		#Stats
		tmp['Stats']=self.user_data['Stats']
		tmp['Stats']['SoftCurrency']+=self.getNumAdd(2386669728)
		tmp['Stats']['ResurrectionTokens']+=self.getNumAdd(4220479132)
		tmp['Stats']['SkillPoints']+=self.getNumAdd(3709963089)
		tmp['Stats']['Power']+=self.getNumAdd(2778961937)
		tmp['Stats']['PVEEnergy']-=self.getNumAdd(2584189485)
		tmp['Stats']['XP']+=self.getNumAdd(2216831597)
		#GlobalStats
		tmp['GlobalStats']=self.user_data['GlobalStats']
		tmp['GlobalStats']['HardCurrency']+=self.getNumAdd(1176006757)
		#VIP
		if 'VIP' in self.user_data:
			tmp['VIP']=self.user_data['VIP']
			tmp['VIP']['VIPTokens']+=self.getNumAdd(3414317992)

		tmp.update(fin_data)
		data['Data']={}
		data['Data']=tmp
		return self.callAPI('UserSave',data)

	def injectStuff(self,Region,Quest,StageIndex,Difficulty,TimesSimmed,Team):
		if not 'Transactions' in self.user_data:
			print 'complete tutorial or check id'
			exit(1)
		tmp={}
		DataTimestamp=int(time.time())
		Timestamp=DataTimestamp+79
		tmp['Transactions']=self.user_data['Transactions']
		trans1=self.addNewTransactions(1648457619,DataTimestamp,Timestamp,True)
		trans1['Verifier']=self.createVerifier(Region,Quest,StageIndex,Difficulty,TimesSimmed,Team,trans1['Credit'])
		tmp['Transactions']['List'].append(trans1)
		tmp['Transactions']['Id']+=len(tmp['Transactions']['List'])
		return self.UserSave(tmp)

	def repeatQuest(self,Region,Quest,StageIndex,Difficulty,TimesSimmed,Team):
		return self.UserSave(tmp)

	def completeQuest(self,Region,Quest,StageIndex,Difficulty,BattleId,Team):
		tmp={}
		DataTimestamp=int(time.time())
		Timestamp=DataTimestamp+79
		BattleId=Timestamp-4
		
		tmp['Transactions']=self.user_data['Transactions']
		trans1=self.addNewTransactions(4122799017,DataTimestamp,Timestamp)
		trans1['Verifier']=self.createVerifier({"Region":Region,"Quest":Quest,"StageIndex":StageIndex,"Difficulty":Difficulty,"BattleId":BattleId})
		tmp['Transactions']['List'].append(trans1)
		
		trans2=self.addNewTransactions(1483281682,DataTimestamp,Timestamp,True)
		trans2['Verifier']=self.createVerifier({"Region":Region,"Quest":Quest,"StageIndex":StageIndex,"Difficulty":Difficulty,"Won":1,"Rating":3,"Team":Team,"NemesisFlag":0,"NemesisAmbush":0,"EnemiesKilled":20,"BodyguardCount":0,"BattleId":BattleId,"MorgulTrait":0,"InitialCredits":[{"Type":2468616184,"Item":2386669728,"Amount":self.getNumAdd(2386669728)},{"Type":2468616184,"Item":1217894615,"Amount":self.getNumAdd(1217894615)},{"Type":2468616184,"Item":1176006757,"Amount":self.getNumAdd(1176006757)},{"Type":2468616184,"Item":2216831597,"Amount":self.getNumAdd(2216831597)}],"InitialMorgulRewards":[]})
		tmp['Transactions']['List'].append(trans2)
		tmp['Transactions']['Id']+=len(tmp['Transactions']['List'])
		return self.UserSave(tmp)
		
	def createNewAccount(self):
		self.setVID(self.genRandomDeviceID())
		self.UserAuth()
		self.UserLoad()
		self.Poll()
		
if __name__ == "__main__":
	a=API()