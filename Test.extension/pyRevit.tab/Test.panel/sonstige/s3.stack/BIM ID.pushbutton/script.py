# coding: utf8
from IGF_log import getlog
from rpw import revit, DB
from pyrevit import script, forms
from System.Collections.ObjectModel import ObservableCollection
from System.Windows import FontWeights, FontStyles, Visibility
from System.Windows.Media import Brushes, BrushConverter
from System.Windows.Forms import OpenFileDialog,DialogResult
from System.Windows.Controls import *
from pyrevit.forms import WPFWindow
from IGF_forms import abfrage
import os

##"8.10 BIM-ID und Bearbeitsungsbereiche (RUB-NA)"
__title__ = "BIM ID"
__doc__ = """
BIM-ID und Bearbeitunsbereich aus excel in Modell schreiben

ergänzt folgenden Bearbeitungsbereiche:
KG420_Wärmeerzeugungsanlagen_Übergreifend
KG410_Sanitärtechnische Anlagen_Übergreifend
KG434_Kälteanlagen_Übergreifen
KG431_Raumlufttechnische Anlagen_Übergreifend
erganzt:IGF_X_Übergreifend

[2022.10.13]
Version: 2.3
"""
__authors__ = "Menghui Zhang"

try:
    getlog(__title__)
except:
    pass

uidoc = revit.uidoc
doc = revit.doc

logger = script.get_logger()
output = script.get_output()

name = doc.ProjectInformation.Name
number = doc.ProjectInformation.Number
app = revit.app
revitversion = app.VersionNumber

bimid_config = script.get_config(name+number+'BIM-ID und Bearbeitsungsbereiche')

muster_bb = ['KG4xx_Musterbereich']

uebergreifend = []

if revitversion == '2020':
    import excel._NPOI_2020 as _NPOI
else:
    import excel._NPOI_2022 as _NPOI

def get_cell_Daten(sheet,r,c):
    """für NPOI"""
    row = sheet.GetRow(r)
    if row:
        cell = row.GetCell(c)
        if cell:
            if cell.CellType.value__ == 0:
                try:return cell.NumericCellValue
                except:return ''
            elif cell.CellType.value__ == 1:
                try:return cell.StringCellValue
                except:
                    try:return cell.RichStringCellValue
                    except:return ''

            elif cell.CellType.value__ == 2:
                try:return cell.StringCellValue
                except:
                    try:return cell.NumericCellValue
                    except:return ''
            elif cell.CellType.value__ == 3:
                return ''
            elif cell.CellType.value__ == 4:
                try:return cell.BooleanCellValue
                except:return ''

            elif cell.CellType.value__ == 5:
                try:return cell.ErrorCellValue
                except:return ''
            return ''
        else:
            return ''
    else:
        return ''

# Bearbeitungsbereich
worksets = DB.FilteredWorksetCollector(doc).OfKind(DB.WorksetKind.UserWorkset)
Workset_dict = {}
for el in worksets:
    Workset_dict[el.Name] = el.Id.ToString()

# Exceldaten
class Exceldaten(object):
    def __init__(self):
        self.checked = False
        self.bb = False
        self.Systemname = None
        self.GK = None
        self.KG = None
        self.KN01 = None
        self.KN02 = None
        self.AnNr = None
        self.AnGeAn = None
        self.PzAT = None
        self.PzAZ = None
        self.SysKZ = None
        self.Sysname = None
        self.BIMID = None
        self.TempW = None
        self.TempS = None
        self.Workset = None
    
    def get_bimid(self):
        self.BIMID = self.GK+'_'+self.KG+'_'+self.KN01+' '+self.KN02

Liste_Luft = ObservableCollection[Exceldaten]()
Liste_Rohr = ObservableCollection[Exceldaten]()
Liste_All = ObservableCollection[Exceldaten]()

def getKN(kn):
    if len(kn) == 0:return '00'
    if len(kn) == 0:return '0' + kn
    if len(kn) == 0:return kn

def datenlesen(filepath):
    fs = _NPOI.FileStream(filepath,_NPOI.FileMode.Open,_NPOI.FileAccess.Read)
    book = _NPOI.np.XSSF.UserModel.XSSFWorkbook(fs)
    sheet = book.GetSheet('Luft')
    rows = sheet.LastRowNum
    
    for row in range(2,rows+1):
        tempclass = Exceldaten()
        sysname = get_cell_Daten(sheet,row,0)
        if sysname == '' or sysname == None:
            continue
        tempclass.Systemname = sysname
        tempclass.GK = get_cell_Daten(sheet,row,1)
        tempclass.KG = str(int(get_cell_Daten(sheet,row,2)))
        tempclass.KN01 = getKN(str(int(get_cell_Daten(sheet,row,3))))
        tempclass.KN02 = getKN(str(int(get_cell_Daten(sheet,row,4))))
        tempclass.AnNr = get_cell_Daten(sheet,row,6)
        tempclass.AnGeAn = get_cell_Daten(sheet,row,7)
        tempclass.TempW = get_cell_Daten(sheet,row,8)
        tempclass.TempS = get_cell_Daten(sheet,row,9)
        tempclass.PzAT = get_cell_Daten(sheet,row,10)
        tempclass.PzAZ = get_cell_Daten(sheet,row,11)
        tempclass.SysKZ = get_cell_Daten(sheet,row,12)
        tempclass.Sysname = get_cell_Daten(sheet,row,13)
        tempclass.Workset = get_cell_Daten(sheet,row,14)
        tempclass.get_bimid()
        Liste_Luft.Add(tempclass)
        Liste_All.Add(tempclass)
    
    sheet = book.GetSheet('Rohr')
    rows = sheet.LastRowNum
    for row in range(2,rows+1):
        tempclass = Exceldaten()
        sysname = get_cell_Daten(sheet,row,0)
        if sysname == '' or sysname == None:
            continue
        tempclass.Systemname = sysname
        tempclass.GK = get_cell_Daten(sheet,row,1)
        tempclass.KG = str(int(get_cell_Daten(sheet,row,2)))
        tempclass.KN01 = getKN(str(int(get_cell_Daten(sheet,row,3))))
        tempclass.KN02 = getKN(str(int(get_cell_Daten(sheet,row,4))))
        tempclass.AnNr = get_cell_Daten(sheet,row,6)
        tempclass.AnGeAn = get_cell_Daten(sheet,row,7)
        tempclass.SysKZ = get_cell_Daten(sheet,row,8)
        tempclass.Sysname = get_cell_Daten(sheet,row,9)
        tempclass.Workset = get_cell_Daten(sheet,row,10)
        tempclass.get_bimid()
        Liste_Rohr.Add(tempclass)
        Liste_All.Add(tempclass)
        
try:
    Adresse = bimid_config.bimid
    if os.path.exists(Adresse):
        try:
            datenlesen(Adresse)
        except Exception as e:
            logger.error(e)
except Exception as e:
    logger.error(e)

# ExcelBimId GUI
class ExcelBimId(WPFWindow):
    def __init__(self, xaml_file_name,liste_Luft,liste_Rohr):
        self.liste_Luft = liste_Luft
        self.liste_Rohr = liste_Rohr
        WPFWindow.__init__(self, xaml_file_name)
        self.tempcoll = ObservableCollection[Exceldaten]()
        self.altdatagrid = None
        self.result = False
        self.read_config()

        try:
            self.dataGrid.ItemsSource = self.liste_Luft
            self.altdatagrid = self.liste_Luft
            self.backAll()
            self.click(self.luft)
        except Exception as e:
            logger.error(e)

        self.systemsuche.TextChanged += self.search_txt_changed
        self.Adresse.TextChanged += self.excel_changed

    def click(self,button):
        button.Background = BrushConverter().ConvertFromString("#FF707070")
        button.FontWeight = FontWeights.Bold
        button.FontStyle = FontStyles.Italic
    def back(self,button):
        button.Background  = Brushes.White
        button.FontWeight = FontWeights.Normal
        button.FontStyle = FontStyles.Normal
    def backAll(self):
        self.back(self.luft)
        self.back(self.rohr)

    def rohre(self,sender,args):
        self.backAll()
        self.click(self.rohr)
        self.dataGrid.ItemsSource = self.liste_Rohr
        self.altdatagrid = self.liste_Rohr
        self.dataGrid.Columns[9].Visibility = Visibility.Hidden
        self.dataGrid.Columns[10].Visibility = Visibility.Hidden
        self.dataGrid.Columns[11].Visibility = Visibility.Hidden
        self.dataGrid.Columns[12].Visibility = Visibility.Hidden
        self.dataGrid.Items.Refresh()

    def luftung(self,sender,args):
        self.backAll()
        self.click(self.luft)
        self.dataGrid.ItemsSource = self.liste_Luft
        self.altdatagrid = self.liste_Luft
        self.dataGrid.Columns[9].Visibility = Visibility.Visible
        self.dataGrid.Columns[10].Visibility = Visibility.Visible
        self.dataGrid.Columns[11].Visibility = Visibility.Visible
        self.dataGrid.Columns[12].Visibility = Visibility.Visible
        self.dataGrid.Items.Refresh()

    def read_config(self):
        try:
            if os.path.exists(bimid_config.bimid):
                self.Adresse.Text = str(bimid_config.bimid)
            else:self.Adresse.Text = bimid_config.bimid = ""

        except:
            self.Adresse.Text = bimid_config.bimid = ""

    def write_config(self):
        bimid_config.bimid = self.Adresse.Text.encode('utf-8')
        script.save_config()

    def search_txt_changed(self, sender, args):
        """Handle text change in search box."""
        self.tempcoll.Clear()
        text_typ = self.systemsuche.Text.upper()
        if text_typ in ['',None]:
            self.dataGrid.ItemsSource = self.altdatagrid

        else:
            if text_typ == None:
                text_typ = ''
            for item in self.altdatagrid:
                if item.Systemname.upper().find(text_typ) != -1:
                    self.tempcoll.Add(item)
            self.dataGrid.ItemsSource = self.tempcoll
        self.dataGrid.Items.Refresh()

    def excel_changed(self, sender, args):
        Liste_Luft.Clear()
        Liste_Rohr.Clear()
        try:
            datenlesen(self.Adresse.Text)
        except:
            pass
        self.liste_Luft = Liste_Luft
        self.dataGrid.ItemsSource = Liste_Luft

    def durchsuchen(self,sender,args):
        dialog = OpenFileDialog()
        dialog.Multiselect = False
        dialog.Title = "BIM-ID Datei suchen"
        dialog.Filter = "Excel Dateien|*.xls;*.xlsx"
        if dialog.ShowDialog() == DialogResult.OK:
            self.Adresse.Text = dialog.FileName
        self.write_config()

    def checkall(self,sender,args):
        for item in self.dataGrid.Items:
            item.checked = True
        self.dataGrid.Items.Refresh()

    def uncheckall(self,sender,args):
        for item in self.dataGrid.Items:
            item.checked = False
        self.dataGrid.Items.Refresh()

    def toggleall(self,sender,args):
        for item in self.dataGrid.Items:
            value = item.checked
            item.checked = not value
        self.dataGrid.Items.Refresh()
    def checkallbb(self,sender,args):
        for item in self.dataGrid.Items:
            item.bb = True
        self.dataGrid.Items.Refresh()

    def uncheckallbb(self,sender,args):
        for item in self.dataGrid.Items:
            item.bb = False
        self.dataGrid.Items.Refresh()

    def toggleallbb(self,sender,args):
        for item in self.dataGrid.Items:
            value = item.bb
            item.bb = not value
        self.dataGrid.Items.Refresh()

    def ok(self,sender,args):
        self.result = True
        self.Close()

windowExcelBimId = ExcelBimId("Window.xaml",Liste_Luft,Liste_Rohr)
try:
    windowExcelBimId.ShowDialog()
except Exception as e:
    logger.error(e)
    windowExcelBimId.Close()
    script.exit()

if windowExcelBimId.result == False:
    script.exit()

muster_bb_bearbeiten = windowExcelBimId.muster.IsChecked
sichtbar = windowExcelBimId.sichtbar.IsChecked
uebergreifend_beruecksichtigt = windowExcelBimId.mehrgewerke.IsChecked

# for el in Liste_All:
#     print(el.bb,el.Systemname,el.GK,el.KG,el.KN01,el.KN02,el.AnNr,el.AnGeAn,el.PzAT,el.PzAZ,el.SysKZ,el.Sysname,el.BIMID,el.TempW,el.TempS,el.Workset)

worksset_Excel = [e.Workset for e in Liste_All if e.checked or e.bb]
worksset_Excel = list(worksset_Excel)
worksset_Excel.append('KG4xx_Übergreifend')
worksset_Excel.append('KG420_Wärmeerzeugungsanlagen_Übergreifend')
worksset_Excel.append('KG410_Sanitärtechnische Anlagen_Übergreifend')
worksset_Excel.append('KG434_Kälteanlagen_Übergreifen')
worksset_Excel.append('KG431_Raumlufttechnische Anlagen_Übergreifend')
fehlendeworkset = []
if len(worksset_Excel) > 0:
    for item in worksset_Excel:
        if not item in Workset_dict.keys():
           fehlendeworkset.append(item)
fehlendeworkset = set(fehlendeworkset)
fehlendeworkset = list(fehlendeworkset)

# Bearbeitungsbereich erstellen
if len(fehlendeworkset) > 0:
    logger.error('folgende Bearbeitungsbereiche fehlt:')
    for e in fehlendeworkset:
        logger.error(e)

    if forms.alert("fehlende Bearbeitungsbereiche erstellen?", ok=False, yes=True, no=True):
        t = DB.Transaction(doc)
        t.Start('Bearbeitungsbereich erstellen')
        for el in fehlendeworkset:
            logger.info(30*'-')
            logger.info(el)
            try:
                item = DB.Workset.Create(doc,el)
                DB.WorksetDefaultVisibilitySettings.SetWorksetVisibility(DB.WorksetDefaultVisibilitySettings.GetWorksetDefaultVisibilitySettings(doc),item.Id,sichtbar)
                Workset_dict[el] = item.Id.ToString()
                logger.info('Bearbeitungsbereich {} erstellt'.format(el))
            except Exception as e:
                logger.error(e)
        doc.Regenerate()
        t.Commit()
        t.Dispose()

# Luft System
luftsysids = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_DuctSystem).WhereElementIsNotElementType().ToElementIds()


# Rohr System
rohrsysids = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_PipingSystem).WhereElementIsNotElementType().ToElementIds()

class MEP_System:
    def __init__(self,System_Excel):
        self.bimid = System_Excel.checked
        self.systemname = System_Excel.Systemname
        self.GK = System_Excel.GK
        self.KG = System_Excel.KG
        self.KN01 = System_Excel.KN01
        self.KN02 = System_Excel.KN02
        self.BIMID = System_Excel.BIMID
        self.AnNr = System_Excel.AnNr
        self.AnGeAn = System_Excel.AnGeAn
        self.SysKZ = System_Excel.SysKZ
        self.Sysname = System_Excel.Sysname
        self.PzAT = System_Excel.PzAT
        self.PzAZ = System_Excel.PzAZ
        self.TempW = System_Excel.TempW
        self.TempS = System_Excel.TempS
        self.Workset = System_Excel.Workset
        self.bb = System_Excel.bb

        try:
            self.PzAT = float(self.PzAT[:self.PzAT.find('%')])/100
        except:
            pass
        
        self.liste_system = []
        self.liste_bauteile = []
        self.typ = None
        self.dict_bauteile_ueber = {}
        self.dict_external = {}
        
    def get_elemente(self):
        for el in self.liste_system:
            systemid = el.Id.ToString()
            try:
                elemente = el.DuctNetwork
            except:
                elemente = el.PipingNetwork

            for elem in elemente:
                cate = elem.Category.Id.ToString()
                # Leitung
                if cate in ['-2008000','-2008020','-2008050','-2008044']:
                    try:
                        if elem.MEPSystem.Id.ToString() == systemid:
                            if elem.Id.ToString() not in self.liste_bauteile:
                                self.liste_bauteile.append(elem.Id.ToString())
                    except:
                        pass
                # Auslass, Sprinkler
                elif cate in ['-2008013','-2008099']:
                    try:
                        if list(elem.MEPModel.ConnectorManager.Connectors)[0].MEPSystem.Id.ToString() == systemid:
                            if elem.Id.ToString() not in self.liste_bauteile:
                                self.liste_bauteile.append(elem.Id.ToString())
                    except:
                        pass
                # Bauteile
                elif cate in ['-2008010','-2008016','-2001140','-2008049','-2008055','-2001160']:
                    conns = elem.MEPModel.ConnectorManager.Connectors
                    In = {}
                    Out = {}
                    Unverbunden = {}
                    for conn in conns:
                        if conn.IsConnected:
                            if conn.Direction.ToString() == 'In':
                                In[conn.Id] = conn
                            else:
                                Out[conn.Id] = conn
                        else:
                            Unverbunden[conn.Id] = conn
                    sorted(In)
                    sorted(Out)
                    sorted(Unverbunden)
                    conns = In.values()[:]
                    connouts = Out.values()[:]
                    connunvers = Unverbunden.values()[:]
                    conns.extend(connouts)
                    conns.extend(connunvers)
                    # if not uebergreifend_beruecksichtigt:
                    try:
                        for conn in conns:
                            if not conn.MEPSystem:
                                continue
                            else:
                                if conn.MEPSystem.Id.ToString() == systemid:
                                    if elem.Id.ToString() not in self.liste_bauteile:
                                        self.liste_bauteile.append(elem.Id.ToString())
                                break
                            
                    except:
                        pass
                    # else:
                    #     systemListe = [systemid] 
                    #     gewerke = []
                    #     try:
                    #         for conn in conns:
                    #             if not conn.MEPSystem:
                    #                 continue
                    #             else:
                    #                 if conn.MEPSystem.Id.ToString() == systemid:
                    #                     if elem.Id.ToString() not in self.liste_bauteile:
                    #                         gewerke.append(self.GK)
                    #                 break
                    #     except:
                    #         pass

                    #     if len(gewerke) > 0:
                    #         try:
                    #             for conn in conns:
                    #                 if not conn.MEPSystem:
                    #                     continue                                        
                    #                 else:
                    #                     systemtyp = conn.MEPSystem.get_Parameter(DB.BuiltInParameter.ELEM_TYPE_PARAM).AsValueString()
                    #                     if conn.MEPSystem.Id.ToString() not in systemListe:
                    #                         systemListe.append(conn.MEPSystem.Id.ToString())
                    #                     try:
                    #                         gewerk = self.dict_external[systemtyp].GK
                    #                         if gewerk and gewerk != None:
                    #                             if gewerk not in gewerke:
                    #                                 gewerke.append(gewerk)
                    #                     except Exception as e:
                    #                         logger.error(e)
                    #         except:
                    #             pass
                    #         if len(gewerke) == 1:
                    #             if len(systemListe) == 1:
                    #                 if elem.Id.ToString() not in self.liste_bauteile:
                    #                     self.liste_bauteile.append(elem.Id.ToString())
                    #             else:
                    #                 if elem.Id.ToString() not in self.dict_bauteile_ueber.keys():
                    #                     self.dict_bauteile_ueber[elem.Id.ToString()] = sorted(gewerke)
                    #         else:
                    #             if elem.Id.ToString() not in self.dict_bauteile_ueber.keys():
                    #                 self.dict_bauteile_ueber[elem.Id.ToString()] = sorted(gewerke)

    def get_systemtyp(self):
        for el in self.liste_system:
            typ = el.get_Parameter(DB.BuiltInParameter.ELEM_TYPE_PARAM).AsElementId()
            self.typ = doc.GetElement(typ)
            break
    
    def wert_schreiben(self, elem, param_name, wert):
        if wert not in [None,""]:
            para = elem.LookupParameter(param_name)
            if para:
                if para.StorageType.ToString() == 'Double':
                    para.SetValueString(str(wert))
                else:
                    para.Set(wert)

    def wert_schreiben_system(self):
        self.wert_schreiben(self.typ,'IGF_X_Gewerkkürzel',str(self.GK))
        self.wert_schreiben(self.typ,'IGF_X_Kostengruppe',int(self.KG))
        self.wert_schreiben(self.typ,'IGF_X_Kennnummer_1',int(self.KN01))
        self.wert_schreiben(self.typ,'IGF_X_Kennnummer_2',int(self.KN02))
        self.wert_schreiben(self.typ,'IGF_X_BIM-ID',str(self.BIMID))
        self.wert_schreiben(self.typ,'IGF_X_SystemName',str(self.Sysname))
        self.wert_schreiben(self.typ,'IGF_X_SystemKürzel',str(self.SysKZ))
        self.wert_schreiben(self.typ,'IGF_X_AnlagenGeräteAnzahl',int(self.AnGeAn))
        self.wert_schreiben(self.typ,'IGF_X_AnlagenNr',int(self.AnNr))
        self.wert_schreiben(self.typ,'IGF_X_AnlagenProzentualAnteil',float(self.PzAT))
        self.wert_schreiben(self.typ,'IGF_X_AnlagenProzentualAnzahl',int(self.PzAZ))
        self.wert_schreiben(self.typ,'IGF_RLT_ZuluftTemperaturSo',str(self.TempS))
        self.wert_schreiben(self.typ,'IGF_RLT_ZuluftTemperaturWi',str(self.TempW))
        
class Bauteil(object):
    def __init__(self,elemid,system):
        self.elemid = DB.ElementId(int(elemid))
        self.elem = doc.GetElement(self.elemid)
        self.system = system
        self.bb = self.elem.LookupParameter('Bearbeitungsbereich').AsValueString()
        try:self.ubergreifend = self.elem.Symbol.LookupParameter('IGF_X_Übergreifend').AsInteger()
        except:self.ubergreifend = 0
        self.typ = self.system.GK
    
    def wert_schreiben(self, elem, param_name, wert):
        if wert not in [None,""]:
            para = elem.LookupParameter(param_name)
            
            if para:
                if para.IsReadOnly:
                    return
                if para.StorageType.ToString() == 'Double':
                    try:
                        para.SetValueString(str(wert))
                    except:
                        logger.error(self.elemid,wert,param_name)
                elif para.StorageType.ToString() == 'Integer':
                    try:
                        para.Set(int(wert))
                    except:
                        logger.error(self.elemid,wert,param_name)
                elif para.StorageType.ToString() == 'String':
                    try:
                        para.Set(str(wert))
                    except:
                        logger.error(self.elemid,wert,param_name)
    
    def GK_schreiben(self):
        if self.ubergreifend == 0:
            self.wert_schreiben(self.elem,'IGF_X_Gewerkkürzel_Exemplar',self.system.GK+'_')
        else:
            typ = self.elem.LookupParameter('IGF_X_Gewerkkürzel_Exemplar').AsString()
            if typ:
                liste = typ.split('_')
                text = ''
                for el in liste:
                    if el:
                        if el != self.typ:
                            text += el + '_' 
                text = self.typ + ' _' + text
            else:
                text = self.typ + '_'
            self.wert_schreiben(self.elem,'IGF_X_Gewerkkürzel_Exemplar',text)
  
    def werte_schreiben_bimid(self):
        self.GK_schreiben()
        self.wert_schreiben(self.elem,'IGF_X_KG_Exemplar',self.system.KG)
        self.wert_schreiben(self.elem,'IGF_X_KN01_Exemplar',self.system.KN01)
        self.wert_schreiben(self.elem,'IGF_X_KN02_Exemplar',self.system.KN02)
        self.wert_schreiben(self.elem,'IGF_X_BIM-ID_Exemplar',self.system.BIMID)

        self.wert_schreiben(self.elem,'IGF_X_AnlagenGeräteAnzahl_Exemplar',self.system.AnGeAn)
        self.wert_schreiben(self.elem,'IGF_X_AnlagenNr_Exemplar',self.system.AnNr)
        self.wert_schreiben(self.elem,'IGF_X_SystemKürzel_Exemplar',self.system.SysKZ)
        self.wert_schreiben(self.elem,'IGF_X_SystemName_Exemplar',self.system.Sysname)

        self.wert_schreiben(self.elem,'IGF_RLT_ZuluftTemperaturSo_Exemplar',self.system.TempS)
        self.wert_schreiben(self.elem,'IGF_RLT_ZuluftTemperaturWi_Exemplar',self.system.TempW)

    def werte_schreiben_BB(self):
        if self.ubergreifend and uebergreifend_beruecksichtigt:
            typ = self.elem.LookupParameter('IGF_X_Gewerkkürzel_Exemplar').AsString()
            if typ:
                liste = typ.split('_')
                if self.typ not in liste:
                    liste.append(self.typ)
            else:
                liste = [self.typ]
            if len(liste) == 1:
                if liste[0] == 'L':
                    Bearbeitungsbereich = Workset_dict['KG431_Raumlufttechnische Anlagen_Übergreifend']
                elif liste[0] == 'K':
                    Bearbeitungsbereich = Workset_dict['KG434_Kälteanlagen_Übergreifend']
                elif liste[0] == 'S':
                    Bearbeitungsbereich = Workset_dict['KG410_Sanitärtechnische Anlagen_Übergreifend']
                elif liste[0] == 'H':
                    Bearbeitungsbereich = Workset_dict['KG420_Wärmeerzeugungsanlagen_Übergreifend']
            else:
                Bearbeitungsbereich = Workset_dict['KG4xx_Übergreifend']
            self.wert_schreiben(self.elem,'Bearbeitungsbereich',int(Bearbeitungsbereich))

        else:
            try:
                self.wert_schreiben(self.elem,'Bearbeitungsbereich',int(Workset_dict[self.system.Workset]))
            except Exception as e:
                logger.error(e)

dict_systeme_alle = {}

dict_systeme = {}

for system in Liste_Luft:
    dict_systeme_alle[system.Systemname] = MEP_System(system)
    if system.checked or system.bb:
        dict_systeme[system.Systemname] = MEP_System(system)
for system in Liste_Rohr:
    dict_systeme_alle[system.Systemname] = MEP_System(system)
    if system.checked or system.bb:
        dict_systeme[system.Systemname] = MEP_System(system)

if len(dict_systeme.keys()) == 0:
    script.exit()

for sysid in luftsysids:
    elem = doc.GetElement(sysid)
    systyp = elem.get_Parameter(DB.BuiltInParameter.ELEM_TYPE_PARAM).AsValueString()
    if systyp in dict_systeme.keys():
        system = dict_systeme[systyp]
        system.liste_system.append(elem)

for sysid in rohrsysids:
    elem = doc.GetElement(sysid)
    systyp = elem.get_Parameter(DB.BuiltInParameter.ELEM_TYPE_PARAM).AsValueString()
    if systyp in dict_systeme.keys():
        system = dict_systeme[systyp]
        system.liste_system.append(elem)

liste = dict_systeme.keys()[:]
liste_neu = []

with forms.ProgressBar(title="{value}/{max_value} Systeme --- Datenermittlung",cancellable=True, step=1) as pb:
    for n,typ in enumerate(liste):
        if pb.cancelled:
            frage_schicht = abfrage(title= __title__,
                    info = 'Vorgang abrechen oder ermittlete Daten behalten?' , 
                    ja = True,ja_text= 'abbrechen',nein_text='weiter').ShowDialog()
            if frage_schicht.antwort == 'abbrechen':
                script.exit()
            else:
                break
        mepsystem = dict_systeme[typ]
        mepsystem.dict_external = dict_systeme_alle
        mepsystem.get_elemente()
        logger.info('{} Elemente in System {}'.format(len(mepsystem.liste_bauteile),mepsystem.systemname))
        liste_neu.append(mepsystem)
        pb.update_progress(n+1,len(liste))


bearbeitet = []
nichtbearbeitet = liste_neu[:]
def main():
    t = DB.Transaction(doc,'BIM-ID')
    t.Start()
    if forms.alert('Daten schreiben?',yes=True,no=True,ok=False):
        with forms.ProgressBar(title='Systeme --- Datene schreiben',cancellable=True, step=10) as pb2:
            for n,mepsystem in enumerate(liste_neu):
                systeme_title = str(mepsystem.systemname) + ' --- ' + str(n+1) + '/' + str(len(liste_neu)) + 'Systeme'
                pb2.title = '{value}/{max_value} Elemente in System ' +  systeme_title
                pb2.step = int((len(mepsystem.liste_bauteile)) /1000) + 10
                mepsystem.get_systemtyp()
                try:
                    mepsystem.wert_schreiben_system()
                except:
                    pass
                for n1,bauteilid in enumerate(mepsystem.liste_bauteile):
                    if pb2.cancelled:
                        if forms.alert('bisherige Änderung behalten?',yes=True,no=True,ok=False):
                            t.Commit()
                            logger.info('Folgenede Systeme sind bereits bearbeitet.')
                            for el in bearbeitet:
                                logger.info(el.systemname)
                            logger.info('---------------------------------------')
                            logger.info('Folgenede Systeme sind nicht bearbeitet.')
                            for el in nichtbearbeitet:
                                logger.info(el.systemname)
                        else:
                            t.RollBack()
                        
                        return
                    bauteil = Bauteil(bauteilid,mepsystem)
                    if bauteil.system.bimid:
                        bauteil.werte_schreiben_bimid()
                    if bauteil.system.bb:
                        if bauteil.bb in muster_bb and not muster_bb_bearbeiten:
                            pass
                        else:
                            bauteil.werte_schreiben_BB()

                    pb2.update_progress(n1+1, len(mepsystem.liste_bauteile))
                bearbeitet.append(mepsystem)
                nichtbearbeitet.remove(mepsystem)
                
    t.Commit()
main()