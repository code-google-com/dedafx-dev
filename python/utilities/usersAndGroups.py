

def getAllDomainUsers(filterTuple=('Administrator', 'Guest', 'sysadmin')):
    import os
    allUsers = []

    if os.name == 'nt':
        import win32net
        import win32netcon
        
        dc = win32net.NetGetAnyDCName (None, None)
        resume = 0
        while 1:
            (_users, total, resume) = win32net.NetUserEnum ( dc, 3, \
                                                             win32netcon.FILTER_NORMAL_ACCOUNT,
                                                             resume, win32netcon.MAX_PREFERRED_LENGTH )
            for _user in _users:
                if _user['name'] in filterTuple:
                    continue
                allUsers.append( {'name':_user['name'], 'full_name':_user['full_name']} )
                
               # if _user['name'] in ('bdeda', 'pharper'):                    
               #     groups = win32net.NetUserGetGroups(dc, _user['name'])
               #     print _user['name'], groups
                    
            if not resume:
                break
    
    elif os.name in ('posix', 'os2'):
        import pwd, grp
        for p in pwd.getpwall():
            _user = pwd.getpwnam(p[0])
            if _user[0] in filterTuple:
                continue
            allUsers.append( {'name':_user[0], 'full_name':_user[4]} ) #, grp.getgrgid(p[3])[0]

        
    return allUsers

def getAllGroups(allUsers):
    """Get and return a list of all the groups in a domain"""
    import os
    allGroups = []
    if os.name == 'nt':
        import win32net
        dc = win32net.NetGetAnyDCName (None, None)
        for _usr in allUsers:
            groups = win32net.NetUserGetGroups(dc, _usr['name'])
            ga = []   
            for g in groups:
                ga.append(g[0])
                if g[0] in allGroups:
                    continue
                allGroups.append(g[0])
            _usr['groups'] = ga
            
    elif os.name in ('posix', 'os2'):
        print 'getAllGroups(au) --> nix not supported yet!'
            
    return allGroups
            

def getActiveUsers(server):
    """Get and return a list of currently active users logged in to the server machine"""
    import os
    import traceback
    import sys
    
    total_list=[]
    
    if os.name == 'nt':
        import win32net
        import win32netcon
        
        res=1  #initially set it to true
        pref=win32netcon.MAX_PREFERRED_LENGTH 
        level=0 #setting it to 1 will provide more detailed info
        
        try:
            while res: #loop until res2
                (user_list,total,res2)=win32net.NetWkstaUserEnum(server,level,res,pref)
                for i in user_list:
                    total_list.append(i['username'])
                res=res2
                return total_list
        except win32net.error:
            
            print traceback.format_tb(sys.exc_info()[2]),'\n',sys.exc_type,'\n',sys.exc_value
            
    elif os.name in ('posix', 'os2'):
        print 'getActiveUsers(server) --> nix not supported yet!'
        
    return total_list

if __name__ == '__main__':
    au = getAllDomainUsers()
    
    for g in getAllGroups(au):
        print g
    
    #print getActiveUsers(r'\\bdeda_Graph')