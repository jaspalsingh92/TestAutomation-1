from Utils.config_loader import Configs

PATHS = Configs.get_test_node("da_installation", "paths")
DZWIN_PATHS = Configs.get_test_node("dz_win_mfa", "paths")

remote_da_root_path = PATHS['remote_da_root_path']
repo_da_root_path = PATHS['repo_da_root_path']

remote_apps_root_path = PATHS['remote_apps_root_path']
repo_apps_root_path = PATHS['repo_apps_root_path']

remote_framework_path = PATHS['remote_framework_path']
remote_da_testscripts_dir = r'.\Tests\CSS\DA\DABAT'
remote_dz_testscripts_dir = r'.\Tests\CSS\DZWin'

remote_testees_root_dir = DZWIN_PATHS['remote_testees_root_dir']
remote_testagent_root_dir = DZWIN_PATHS['remote_testagent_root_dir']
remote_testframework_root_dir = DZWIN_PATHS['remote_testframework_root_dir']
remote_testscripts_root_dir = DZWIN_PATHS['remote_testscripts_root_dir']

remote_da_administrator_console_path = remote_da_root_path + r'\DirectAudit\Console\Centrify DirectAudit Administrator Console64.msi'
repo_da_administrator_console_path = repo_da_root_path + r'\DirectAudit\Console\Centrify DirectAudit Administrator Console64.msi'
da_administrator_startup_path = r'C:\Program Files\Centrify\Audit\AuditManager\Centrify Audit Manager.msc'

remote_da_auditor_path = remote_da_root_path + r'\DirectAudit\Console\Centrify DirectAudit Auditor Console64.msi'
repo_da_auditor_path = repo_da_root_path + r'\DirectAudit\Console\Centrify DirectAudit Auditor Console64.msi'
da_auditor_startup_path = r'C:\Program Files\Centrify\Audit\AuditAnalyzer\Centrify Audit Analyzer.msc'

remote_audit_manager_path = remote_da_root_path + r'\DirectAudit\Audit Management Server\Centrify DirectAudit Audit Management Server64.msi'
repo_audit_manager_path = repo_da_root_path + r'\DirectAudit\Audit Management Server\Centrify DirectAudit Audit Management Server64.msi'
audit_manager_startup_path = r'C:\Program Files\Centrify\Audit\AuditManagementServer\AuditManagementServer.configure.exe'

repo_python_path = repo_apps_root_path + r'\python-3.9.0-amd64.exe'
remote_python_path = remote_apps_root_path + r'\python-3.9.0-amd64.exe'
python_install_path = r'C:\Users\Default\AppData\Local\Programs\Python'


remote_winappdriver_path = remote_apps_root_path + r'\WindowsApplicationDriver.msi'
repo_winappdriver_path = repo_apps_root_path + r'\WindowsApplicationDriver.msi'
remote_winappdriver_startup_path = r'C:\Program Files (x86)\Windows Application Driver\WinAppDriver.exe'

repo_da_agent_path = repo_da_root_path + r'\DirectAudit\Agent\Centrify Agent for Windows64.msi'
remote_da_agent_start_path = r'C:\Program Files\Centrify\Centrify Agent for Windows\Centrify.WinAgent.ServiceConfig.exe'
remote_da_agent_path = remote_da_root_path + r'\DirectAudit\Agent\Centrify Agent for Windows64.msi'

repo_collector_path = repo_da_root_path + r'\DirectAudit\Collector\Centrify DirectAudit Collector64.msi'
remote_collector_path = remote_da_root_path + r'\DirectAudit\Collector\Centrify DirectAudit Collector64.msi'
collector_startup_path = r'C:\Program Files\Centrify\Audit\Collector\collector.configure.exe'

remote_testees_dir = remote_testees_root_dir + r'\release'
remote_testagent_dir = remote_testagent_root_dir + r'\testagent'
remote_testframework_dir = remote_testframework_root_dir + r'\framework'
remote_testscripts_dir = remote_testscripts_root_dir + r'\framework\Tests\CSS'

services_startup_path = r'C:\Windows\system32\services.msc'
wf_advanced_security_startup_path = r'C:\Windows\system32\WF.msc'
event_viewer_startup_path = r'C:\Windows\system32\eventvwr.msc'
cmd_startup_path = r'C:\Windows\system32\cmd.exe'
rdp_startup_path = r'C:\Windows\system32\mstsc.exe'
task_scheduler_startup_path = r'C:\Windows\system32\taskschd.msc'
ie_startup_path = r'C:\Program Files\Internet Explorer\iexplore.exe'
notepad_startup_path = r'C:\Windows\system32\notepad.exe'
powershell_startup_path = r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'