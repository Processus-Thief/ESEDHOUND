# This file is part of ntdsxtract.
#
# ntdsxtract is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ntdsxtract is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ntdsxtract.  If not, see <http://www.gnu.org/licenses/>.

'''
@author:        Csaba Barta
@license:       GNU General Public License 2.0 or later
@contact:       csaba.barta@gmail.com
'''
from ntds import dsfielddictionary
from ntds.dsdatabase import *
from ntds.dslink import *
from ntds.dsrecord import *
from ntds.dstime import *
from ntds.dsencryption import *

from lib.guid import *
from lib.sid import *
from lib.dump import *

class dsObject:
    '''
    The main AD class
    '''
    Record      = None
    Name        = ""
    RecordId    = -1
    TypeId      = -1
    Type        = ""
    GUID        = None
    WhenCreated = -1
    WhenChanged = -1
    USNCreated  = -1
    USNChanged  = -1
    IsDeleted   = False
    
    def __init__(self, dsDatabase, dsRecordId):
        '''
        Constructor
        '''
        self.RecordId = dsRecordId
        self.Record = dsGetRecordByRecordId(dsDatabase, self.RecordId)
        if self.Record == None:
            raise BaseException
        self.Name   = self.Record[dsfielddictionary.dsObjectName2Index]
        self.TypeId = dsGetRecordType(dsDatabase, self.RecordId)
        self.Type   = dsGetTypeName(dsDatabase, self.TypeId)

        if self.Record[dsfielddictionary.dsObjectGUIDIndex] != "":
            self.GUID = GUID(self.Record[dsfielddictionary.dsObjectGUIDIndex])
        
        if self.Record[dsfielddictionary.dsWhenCreatedIndex] != "":
            self.WhenCreated = dsConvertToDSTimeStamp(
                                self.Record[dsfielddictionary.dsWhenCreatedIndex]
                                                      )
        else:
            self.WhenCreated = dsConvertToDSTimeStamp(
                                self.Record[dsfielddictionary.dsRecordTimeIndex]
                                                      )
        
        if self.Record[dsfielddictionary.dsWhenChangedIndex] != "":
            self.WhenChanged = dsConvertToDSTimeStamp(
                                self.Record[dsfielddictionary.dsWhenChangedIndex]
                                                      )

        if self.Record[dsfielddictionary.dsUSNCreatedIndex] != "":
            self.USNCreated = int(self.Record[dsfielddictionary.dsUSNCreatedIndex])
        
        if self.Record[dsfielddictionary.dsUSNChangedIndex] != "":
            self.USNChanged = int(self.Record[dsfielddictionary.dsUSNChangedIndex])
            
        if self.Record[dsfielddictionary.dsIsDeletedIndex] != "":
            self.IsDeleted = True
            
    def getChilds(self):
        '''
        Returns the child objects
        '''
        try:
            childlist = dsMapChildsByRecordId[self.RecordId]
            return childlist
        except:
            return []

    def getAncestors(self, dsDatabase):
        '''
        Returns the ancestors
        '''
        ancestorlist = []
        ancestorvalue = self.Record[dsfielddictionary.dsAncestorsIndex] 
        if ancestorvalue != "":
            l = len(ancestorvalue) / 8
            for aid in range(0, round(l)):
                (ancestorid,) = unpack('I', unhexlify(ancestorvalue[aid * 8:aid * 8 + 8]))
                ancestor = dsObject(dsDatabase, ancestorid)
                if ancestor == None:
                    continue
                ancestorlist.append(ancestor)
        return ancestorlist
            
class dsFVERecoveryInformation(dsObject):
    '''
    The class used for representing BitLocker recovery information stored in AD
    '''
    RecoveryGUID = None
    VolumeGUID = None
    RecoveryPassword = ""
    FVEKeyPackage = ""
    
    def __init__(self, dsDatabase, dsRecordId):
        '''
        Constructor
        '''
        dsObject.__init__(self, dsDatabase, dsRecordId)
        if self.Record[dsfielddictionary.dsRecoveryGUIDIndex] != "":
            self.RecoveryGUID = GUID(self.Record[dsfielddictionary.dsRecoveryGUIDIndex])
        if self.Record[dsfielddictionary.dsVolumeGUIDIndex] != "":
            self.VolumeGUID = GUID(self.Record[dsfielddictionary.dsVolumeGUIDIndex])
        self.RecoveryPassword = self.Record[dsfielddictionary.dsRecoveryPasswordIndex]
        self.FVEKeyPackage = self.Record[dsfielddictionary.dsFVEKeyPackageIndex]
        
        
                
class dsAccount(dsObject):
    '''
    The main account class
    '''
    SID                = None
    SAMAccountName     = ""
    PrincipalName  = ""
    SAMAccountType     = -1
    UserAccountControl = -1
    LogonCount         = -1
    LastLogon          = -1
    LastLogonTimeStamp = -1
    PasswordLastSet    = -1
    AccountExpires     = -1
    BadPwdTime         = -1
    SupplementalCredentials = ""
    PrimaryGroupID     = -1
    BadPwdCount        = -1
    
    def __init__(self, dsDatabase, dsRecordId):
        '''
        Constructor
        '''
        dsObject.__init__(self, dsDatabase, dsRecordId)
        
        self.SID = SID(self.Record[dsfielddictionary.dsSIDIndex])
        self.SAMAccountName = self.Record[dsfielddictionary.dsSAMAccountNameIndex]
        self.PrincipalName = self.Record[dsfielddictionary.dsUserPrincipalNameIndex]
        if self.Record[dsfielddictionary.dsSAMAccountTypeIndex] != "":
            self.SAMAccountType = int(self.Record[dsfielddictionary.dsSAMAccountTypeIndex])
        if self.Record[dsfielddictionary.dsUserAccountControlIndex] != "":
            self.UserAccountControl = int(self.Record[dsfielddictionary.dsUserAccountControlIndex])
        if self.Record[dsfielddictionary.dsPrimaryGroupIdIndex] != "":
            self.PrimaryGroupID = int(self.Record[dsfielddictionary.dsPrimaryGroupIdIndex])
        if self.Record[dsfielddictionary.dsLogonCountIndex] != "":
            self.LogonCount = int(self.Record[dsfielddictionary.dsLogonCountIndex])
        else:
            self.BadPwdCount = -1
        if self.Record[dsfielddictionary.dsBadPwdCountIndex] != "":
            self.BadPwdCount = int(self.Record[dsfielddictionary.dsBadPwdCountIndex])
        else:
            self.BadPwdCount = -1
                        
        self.LastLogon = dsVerifyDSTimeStamp(self.Record[dsfielddictionary.dsLastLogonIndex])
        
        self.LastLogonTimeStamp = dsVerifyDSTimeStamp(self.Record[dsfielddictionary.dsLastLogonTimeStampIndex])
        
        self.PasswordLastSet = dsVerifyDSTimeStamp(self.Record[dsfielddictionary.dsPasswordLastSetIndex])
        
        self.AccountExpires = dsVerifyDSTimeStamp(self.Record[dsfielddictionary.dsAccountExpiresIndex])
        
        self.BadPwdTime = dsVerifyDSTimeStamp(self.Record[dsfielddictionary.dsBadPwdTimeIndex])
    
    def getPasswordHashes(self):
        lmhash = ""
        nthash = ""
        enclmhash = unhexlify(self.Record[dsfielddictionary.dsLMHashIndex][16:])
        encnthash = unhexlify(self.Record[dsfielddictionary.dsNTHashIndex][16:])
        if enclmhash != '':
            lmhash = dsDecryptWithPEK(dsfielddictionary.dsPEK, enclmhash)
            lmhash = hexlify(dsDecryptSingleHash(self.SID.RID, lmhash))
            if lmhash == '':
                lmhash = "NO PASSWORD"
        if encnthash != '':
            nthash = dsDecryptWithPEK(dsfielddictionary.dsPEK, encnthash)
            nthash = hexlify(dsDecryptSingleHash(self.SID.RID, nthash))
            if nthash == '':
                nthash = "NO PASSWORD"
        return (lmhash, nthash)
    
    def getPasswordHistory(self):
        lmhistory = []
        nthistory = []
        enclmhistory = unhexlify(self.Record[dsfielddictionary.dsLMHashHistoryIndex][16:])
        encnthistory = unhexlify(self.Record[dsfielddictionary.dsNTHashHistoryIndex][16:])
        slmhistory = dsDecryptWithPEK(dsfielddictionary.dsPEK, enclmhistory)
        snthistory = dsDecryptWithPEK(dsfielddictionary.dsPEK, encnthistory)
        if slmhistory != "":
            for hindex in range(0,len(slmhistory)/16):
                lmhash   = dsDecryptSingleHash(self.SID.RID, slmhistory[hindex*16:(hindex+1)*16])
                if lmhash == '':
                    lmhistory.append('NO PASSWORD')
                else:
                    lmhistory.append(hexlify(lmhash))
        if snthistory != "":
            for hindex in range(0,len(snthistory)/16):
                nthash = dsDecryptSingleHash(self.SID.RID, snthistory[hindex*16:(hindex+1)*16])
                if nthash == '':
                    nthistory.append('NO PASSWORD')
                else:
                    nthistory.append(hexlify(nthash))
        return (lmhistory, nthistory)
    
    def getSupplementalCredentials(self):
        self.SupplementalCredentials = self.Record[dsfielddictionary.dsSupplementalCredentialsIndex]
        if self.SupplementalCredentials != "":
            tmp = unhexlify(self.SupplementalCredentials[16:])
            tmpdec = dsDecryptWithPEK(dsfielddictionary.dsPEK, tmp)
            return dsSupplCredentials(tmpdec)
        else:
            return None
    
    def getSAMAccountType(self):
        if self.SAMAccountType != -1:
            if self.SAMAccountType & int("0x30000001", 16) == int("0x30000001", 16):
                return "SAM_MACHINE_ACCOUNT"
            if self.SAMAccountType & int("0x30000002", 16) == int("0x30000002", 16):
                return "SAM_TRUST_ACCOUNT"
            if self.SAMAccountType & int("0x30000000", 16) == int("0x30000000", 16):
                return "SAM_NORMAL_USER_ACCOUNT"
            if self.SAMAccountType & int("0x10000001", 16) == int("0x10000001", 16):
                return "SAM_NON_SECURITY_GROUP_OBJECT"
            if self.SAMAccountType & int("0x10000000", 16) == int("0x10000000", 16):
                return "SAM_GROUP_OBJECT"
            if self.SAMAccountType & int("0x20000001", 16) == int("0x20000001", 16):
                return "SAM_NON_SECURITY_ALIAS_OBJECT"
            if self.SAMAccountType & int("0x20000000", 16) == int("0x20000000", 16):
                return "SAM_ALIAS_OBJECT"
            if self.SAMAccountType & int("0x40000001", 16) == int("0x40000001", 16):
                return "SAM_APP_QUERY_GROUP"
            if self.SAMAccountType & int("0x40000000", 16) == int("0x40000000", 16):
                return "SAM_APP_BASIC_GROUP"
        else:
            return ""

    def getUserAccountControl(self):
        uac = []
        if self.UserAccountControl != -1:
            if self.UserAccountControl & int("0x2", 16) == int("0x2", 16):
                uac.append("Disabled")
            if self.UserAccountControl & int("0x10", 16) == int("0x10", 16):
                uac.append("Locked")
            if self.UserAccountControl & int("0x20", 16) == int("0x20", 16):
                uac.append("PWD Not Required")
            if self.UserAccountControl & int("0x40", 16) == int("0x40", 16):
                uac.append("User cannot change PWD")
            if self.UserAccountControl & int("0x80", 16)== int("0x80", 16):
                uac.append("Encrypted clear text PWD allowed")
            if self.UserAccountControl & int("0x200", 16) == int("0x200", 16):
                uac.append("NORMAL_ACCOUNT")
            if self.UserAccountControl & int("0x800", 16) == int("0x800", 16) :
                uac.append("INTERDOMAIN_TRUST_ACCOUNT")
            if self.UserAccountControl & int("0x1000", 16) == int("0x1000", 16):
                uac.append("WORKSTATION_TRUST_ACCOUNT")
            if self.UserAccountControl & int("0x2000", 16) == int("0x2000", 16):
                uac.append("SERVER_TRUST_ACCOUNT")
            if self.UserAccountControl & int("0x10000", 16) == int("0x10000", 16):
                uac.append("PWD Never Expires")
            if self.UserAccountControl & int("0x40000", 16) == int("0x40000", 16):
                uac.append("Smartcard Required")
            if self.UserAccountControl & int("0x800000", 16) == int("0x800000", 16):
                uac.append("PWD Expired")
        return uac
    
    def getMemberOf(self):
        grouplist = []
        try:
            grouplist = dsMapBackwardLinks[self.RecordId]
            return grouplist
        except KeyError:
            return []
        

class dsUser(dsAccount):
    '''
    The class used for representing User objects stored in AD
    '''
    Certificate = ""
    
    def __init__(self, dsDatabase, dsRecordId):
        '''
        Constructor
        '''
        dsAccount.__init__(self, dsDatabase, dsRecordId)
        if self.Record[dsfielddictionary.dsADUserObjectsIndex] != "":
            self.Certificate = unhexlify(self.Record[dsfielddictionary.dsADUserObjectsIndex])
        
class dsComputer(dsAccount):
    '''
    The class used for representing Computer objects stored in AD
    '''
    DNSHostName = ""
    OSName = ""
    OSVersion = ""

    def __init__(self, dsDatabase, dsRecordId):
        '''
        Constructor
        '''
        dsAccount.__init__(self, dsDatabase, dsRecordId)
        self.DNSHostName = self.Record[dsfielddictionary.dsDNSHostNameIndex]
        self.OSName = self.Record[dsfielddictionary.dsOSNameIndex]
        self.OSVersion = self.Record[dsfielddictionary.dsOSVersionIndex]
    
    def getRecoveryInformations(self, dsDatabase):
        rinfos = []
        childlist = self.getChilds()
        for child in childlist:
            if dsGetRecordType(dsDatabase, child) == dsGetTypeIdByTypeName(dsDatabase, "ms-FVE-RecoveryInformation"):
                rinfos.append(dsFVERecoveryInformation(dsDatabase, child))
        return rinfos
    
class dsGroup(dsObject):
    '''
    The class used for representing Group objects stored in AD
    '''
    SID     = None
    
    def __init__(self, dsDatabase, dsRecordId):
        '''
        Constructor
        '''
        dsObject.__init__(self, dsDatabase, dsRecordId)
        self.SID = SID(self.Record[dsfielddictionary.dsSIDIndex])
    
    def getMembers(self):
        memberlist = []
        try:
            memberlist = dsMapLinks[self.RecordId]
            return memberlist
        except KeyError:
            return []

class dsKerberosKey:
    IterationCount = None
    # for list of encryption codes see NTSecAPI.h header in Microsoft SDK
    # normally you'll see the following codes:
    #define KERB_ETYPE_DES_CBC_MD5      3
    #define KERB_ETYPE_AES128_CTS_HMAC_SHA1_96    17
    #define KERB_ETYPE_AES256_CTS_HMAC_SHA1_96    18
    #define KERB_ETYPE_RC4_PLAIN        -140
    KeyType = None
    Key = None
    
class dsKerberosNewKeys:
    DefaultSalt = None
    Credentials = None
    OldCredentials = None
    OlderCredentials = None
    def __init__(self):
        self.Credentials = []
        self.OldCredentials = []
        self.OlderCredentials = []
        
    def Print(self, indent=""):
        print("{0}salt: {1}".format(indent, self.DefaultSalt))
        if len(self.Credentials) > 0:
            print("{0}Credentials".format(indent))
            for key in self.Credentials:
                print("{0}  {1} {2}".format(indent, key.KeyType, hexlify(key.Key)))
        if len(self.OldCredentials) > 0:
            print("{0}OldCredentials".format(indent))
            for key in self.OldCredentials:
                print("{0}  {1} {2}".format(indent, key.KeyType, hexlify(key.Key)))
        if len(self.OlderCredentials) > 0:
            print("{0}OlderCredentials".format(indent))
            for key in self.OlderCredentials:
                print("{0}  {1} {2}".format(indent, key.KeyType, hexlify(key.Key)))

class dsSupplCredentials:
    '''
    Supplemental credentials structures are documented in
    http://msdn.microsoft.com/en-us/library/cc245499.aspx
    '''
    def __init__(self, text):
        self.KerberosNewerKeys = None
        self.KerberosKeys = None
        self.WDigestHashes = None
        self.Packages = None
        self.Password = None
        self.Text = text
        self.ParseUserProperties(text)
    
    def Print(self, indent=""):
        if self.KerberosNewerKeys != None:
            print("{0}Kerberos newer keys".format(indent))
            self.KerberosNewerKeys.Print(indent + "  ")
        if self.KerberosKeys != None:
            print("{0}Kerberos keys".format(indent))
            self.KerberosKeys.Print(indent + "  ")
        if self.WDigestHashes != None:
            print("{0}WDigest hashes".format(indent))
            for h in self.WDigestHashes:
                print("{0}  {1}".format(indent, hexlify(h)))
        if self.Packages != None:
            print("{0}Packages".format(indent))
            for p in self.Packages:
                print("{0}  {1}".format(indent, p))
        if self.Password != None:
            print("{0}Password: {1}".format(indent, self.Password))
        print("Debug: ")
        print(dump(self.Text,16,16))
    
    def ParseUserProperties(self, text):
        offset = 0
        reserved1 = unpack('I', text[offset:offset+4])[0]
        assert reserved1 == 0
        offset += 4
        lengthOfStructure = unpack('I', text[offset:offset+4])[0]
        assert len(text) == lengthOfStructure + 3*4 + 1
        offset += 4
        reserved2 = unpack('H', text[offset:offset+2])[0]
        assert reserved2 == 0
        offset += 2
        reserved3 = unpack('H', text[offset:offset+2])[0]
        assert reserved3 == 0
        offset += 2
        offset += 96 # reserved4
        PropertySignature = unpack('H', text[offset:offset+2])[0]
        assert PropertySignature == 0x50
        offset += 2
        # The number of USER_PROPERTY elements in the UserProperties field.
        PropertyCount = unpack('H', text[offset:offset+2])[0]
        offset += 2
        for i in range(PropertyCount):
            offset = self.ParseUserProperty(text, offset)
        assert offset == len(text) - 1
        reserved5 = ord(text[offset:offset+1])
        # must be 0 according to documentation, but in practice contains arbitrary value
        #assert reserved5 == 0
  
    def ParseUserProperty(self, text, offset):
        NameLength = unpack('H', text[offset:offset+2])[0]
        offset += 2
        ValueLength = unpack('H', text[offset:offset+2])[0]
        offset += 2
        reserved = unpack('H', text[offset:offset+2])[0]
        offset += 2
        Name = text[offset:offset+NameLength].decode('utf-16')
        offset += NameLength
        if Name == u"Primary:Kerberos-Newer-Keys":
            self.KerberosNewerKeys = self.ParseKerberosNewerKeysPropertyValue(unhexlify(text[offset:offset+ValueLength]))
        elif Name == u"Primary:Kerberos":
            self.KerberosKeys = self.ParseKerberosPropertyValue(unhexlify(text[offset:offset+ValueLength]))
        elif Name == u"Primary:WDigest":
            self.WDigestHashes = self.ParseWDigestPropertyValue(unhexlify(text[offset:offset+ValueLength]))
        elif Name == u"Packages":
            self.Packages = unhexlify(text[offset:offset+ValueLength]).decode('utf-16').split("\x00")
        elif Name == u"Primary:CLEARTEXT":
            self.Password = unhexlify(text[offset:offset+ValueLength]).decode('utf-16')
        else:
            print(Name)
        return offset + ValueLength

    def ParseWDigestPropertyValue(self, text):
        try:
            offset = 0
            Reserved1 = ord(text[offset:offset+1])
            offset += 1
            Reserved2 = ord(text[offset:offset+1])
            assert Reserved2 == 0
            offset += 1
            Version = ord(text[offset:offset+1])
            assert Version == 1
            offset += 1
            NumberOfHashes = ord(text[offset:offset+1])
            assert NumberOfHashes == 29
            offset += 1
            for i in range(3):
                Reserved3 = unpack('I', text[offset:offset+4])[0]
                assert Reserved3 == 0
                offset += 4
            hashes = []
            for i in range(NumberOfHashes):
                hashes.append(text[offset:offset+16])
                offset += 16
            return hashes
        except:
            return None
    
    def ParseKerberosNewerKeysPropertyValue(self, text):
        try:
            offset = 0
            keys = dsKerberosNewKeys()
            Revision = unpack('H', text[offset:offset+2])[0]
            assert Revision == 4
            offset += 2
            Flags = unpack('H', text[offset:offset+2])[0]
            assert Flags == 0
            offset += 2
            CredentialCount = unpack('H', text[offset:offset+2])[0]
            offset += 2
            ServiceCredentialCount = unpack('H', text[offset:offset+2])[0]
            assert ServiceCredentialCount == 0
            offset += 2
            OldCredentialCount = unpack('H', text[offset:offset+2])[0]
            offset += 2
            OlderCredentialCount = unpack('H', text[offset:offset+2])[0]
            offset += 2
            DefaultSaltLength = unpack('H', text[offset:offset+2])[0]
            offset += 2
            DefaultSaltMaximumLength = unpack('H', text[offset:offset+2])[0]
            offset += 2
            DefaultSaltOffset = unpack('I', text[offset:offset+4])[0]
            offset += 4
            DefaultIterationCount = unpack('I', text[offset:offset+4])[0]
            offset += 4
            for i in range(CredentialCount):
                offset, key = self.KerberosKeyDataNew(text, offset)
                keys.Credentials.append(key)
            for i in range(OldCredentialCount):
                offset, key = self.KerberosKeyDataNew(text, offset)
                keys.OldCredentials.append(key)
            for i in range(OlderCredentialCount):
                offset, key = self.KerberosKeyDataNew(text, offset)
                keys.OlderCredentials.append(key)
            # + one blank KeyDataNew record. Record length is 24 bytes,
            offset += 24
            assert offset == DefaultSaltOffset
            keys.DefaultSalt = text[offset:offset+DefaultSaltMaximumLength].decode("utf-16")
            return keys
        except:
            return None

    def ParseKerberosPropertyValue(self, text):
        try:
            offset = 0
            keys = dsKerberosNewKeys()
            Revision = unpack('H', text[offset:offset+2])[0]
            assert Revision == 3
            offset += 2
            Flags = unpack('H', text[offset:offset+2])[0]
            assert Flags == 0
            offset += 2
            CredentialCount = unpack('H', text[offset:offset+2])[0]
            offset += 2
            OldCredentialCount = unpack('H', text[offset:offset+2])[0]
            offset += 2
            DefaultSaltLength = unpack('H', text[offset:offset+2])[0]
            offset += 2
            DefaultSaltMaximumLength = unpack('H', text[offset:offset+2])[0]
            offset += 2
            DefaultSaltOffset = unpack('I', text[offset:offset+4])[0]
            offset += 4
            for i in range(CredentialCount):
                offset, key = self.KerberosKeyData(text, offset)
                keys.Credentials.append(key)
            for i in range(OldCredentialCount):
                offset, key = self.KerberosKeyData(text, offset)
                keys.OldCredentials.append(key)
            # + one blank KeyDataNew record. Record length is 20 bytes,
            offset += 20
            assert offset == DefaultSaltOffset
            keys.DefaultSalt = text[offset:offset+DefaultSaltMaximumLength].decode("utf-16")
            return keys
        except:
            return None

    def KerberosKeyDataNew(self, text, offset):
        try:
            key = dsKerberosKey()
            Reserved1 = unpack('H', text[offset:offset+2])[0]
            assert Reserved1 == 0
            offset += 2
            Reserved2 = unpack('H', text[offset:offset+2])[0]
            assert Reserved2 == 0
            offset += 2
            Reserved3 = unpack('I', text[offset:offset+4])[0]
            assert Reserved3 == 0
            offset += 4
            key.IterationCount = unpack('I', text[offset:offset+4])[0]
            offset += 4
            key.KeyType = unpack('i', text[offset:offset+4])[0]
            offset += 4
            KeyLength = unpack('I', text[offset:offset+4])[0]
            offset += 4
            KeyOffset = unpack('I', text[offset:offset+4])[0]
            offset += 4
            key.Key = text[KeyOffset:KeyOffset+KeyLength]
            return offset, key
        except:
            return None
    
    def KerberosKeyData(self, text, offset):
        try:
            key = dsKerberosKey()
            Reserved1 = unpack('H', text[offset:offset+2])[0]
            assert Reserved1 == 0
            offset += 2
            Reserved2 = unpack('H', text[offset:offset+2])[0]
            assert Reserved2 == 0
            offset += 2
            Reserved3 = unpack('I', text[offset:offset+4])[0]
            assert Reserved3 == 0
            offset += 4
            key.KeyType = unpack('i', text[offset:offset+4])[0]
            offset += 4
            KeyLength = unpack('I', text[offset:offset+4])[0]
            offset += 4
            KeyOffset = unpack('I', text[offset:offset+4])[0]
            offset += 4
            key.Key = text[KeyOffset:KeyOffset+KeyLength]
            return offset, key
        except:
            return None
    
