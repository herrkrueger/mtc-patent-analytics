class config:

    def connect_to_database(self):
        reqsD={
            'drivername' : 'postgresql',
            'host' : 'localhost',
            'port' : '5432',
            #'username' : 'patent_classification_user',
            #'password' : 'mtc'
            #'database' : 'patent-classification'
        }
    
        return reqsD

    def files(self):
        fileD={
            'cpc' : 'https://www.wipo.int/ipc/itos4ipc/ITSupport_and_download_area//20190101/CPC2IPC/subCPC2IPClike_scheme_20190801_20190101_20190910.zip',
            'cpc_en' : 'https://www.cooperativepatentclassification.org/cpc/interleaved/CPCTitleList201908.zip',
            'ipc' : 'https://www.wipo.int/ipc/itos4ipc/ITSupport_and_download_area//20190101/MasterFiles/ipc_scheme_20190101.zip',
            'ipc_en' : ['https://www.wipo.int/ipc/itos4ipc/ITSupport_and_download_area/20190101/IPC_scheme_title_list/EN_ipc_section_A_title_list_20190101.txt',
        'https://www.wipo.int/ipc/itos4ipc/ITSupport_and_download_area/20190101/IPC_scheme_title_list/EN_ipc_section_B_title_list_20190101.txt',
        'https://www.wipo.int/ipc/itos4ipc/ITSupport_and_download_area/20190101/IPC_scheme_title_list/EN_ipc_section_C_title_list_20190101.txt',
        'https://www.wipo.int/ipc/itos4ipc/ITSupport_and_download_area/20190101/IPC_scheme_title_list/EN_ipc_section_D_title_list_20190101.txt',
        'https://www.wipo.int/ipc/itos4ipc/ITSupport_and_download_area/20190101/IPC_scheme_title_list/EN_ipc_section_E_title_list_20190101.txt',
        'https://www.wipo.int/ipc/itos4ipc/ITSupport_and_download_area/20190101/IPC_scheme_title_list/EN_ipc_section_F_title_list_20190101.txt',
        'https://www.wipo.int/ipc/itos4ipc/ITSupport_and_download_area/20190101/IPC_scheme_title_list/EN_ipc_section_G_title_list_20190101.txt',
        'https://www.wipo.int/ipc/itos4ipc/ITSupport_and_download_area/20190101/IPC_scheme_title_list/EN_ipc_section_H_title_list_20190101.txt'],
            'ipc_fr' : ['https://www.wipo.int/ipc/itos4ipc/ITSupport_and_download_area/20190101/IPC_scheme_title_list/FR_ipc_section_A_title_list_20190101.txt',
            'https://www.wipo.int/ipc/itos4ipc/ITSupport_and_download_area/20190101/IPC_scheme_title_list/FR_ipc_section_B_title_list_20190101.txt',
            'https://www.wipo.int/ipc/itos4ipc/ITSupport_and_download_area/20190101/IPC_scheme_title_list/FR_ipc_section_C_title_list_20190101.txt',
            'https://www.wipo.int/ipc/itos4ipc/ITSupport_and_download_area/20190101/IPC_scheme_title_list/FR_ipc_section_D_title_list_20190101.txt',
            'https://www.wipo.int/ipc/itos4ipc/ITSupport_and_download_area/20190101/IPC_scheme_title_list/FR_ipc_section_E_title_list_20190101.txt',
            'https://www.wipo.int/ipc/itos4ipc/ITSupport_and_download_area/20190101/IPC_scheme_title_list/FR_ipc_section_F_title_list_20190101.txt',
            'https://www.wipo.int/ipc/itos4ipc/ITSupport_and_download_area/20190101/IPC_scheme_title_list/FR_ipc_section_G_title_list_20190101.txt',
            'https://www.wipo.int/ipc/itos4ipc/ITSupport_and_download_area/20190101/IPC_scheme_title_list/FR_ipc_section_H_title_list_20190101.txt'
            ],
            'ipc_de' : '',
            'cpc_to_ipc' : 'https://www.cooperativepatentclassification.org/cpcConcordances/CPCtoIPCxmlAugust2019.xml',
            'ipc_inventory' : 'http://www.wipo.int/ipc/itos4ipc/ITSupport_and_download_area/20190101/IPC_symbol_inventory/20190101_inventory_of_IPC_ever_used_symbols.csv',
            'cpc_inventory' : 'https://www.cooperativepatentclassification.org/cpc/interleaved/CPCValidityFile201908.zip',
            'ipc_statistics' : 'http://www.wipo.int/ipc/itos4ipc/ITSupport_and_download_area/20190101/stats/IPC_statistics-20190101_V2.0.zip'
        }
        return fileD
