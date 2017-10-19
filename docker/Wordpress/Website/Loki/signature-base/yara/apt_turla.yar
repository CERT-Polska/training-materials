/*
	Yara Rule Set
	Author: Florian Roth
	Date: 2016-06-09
	Identifier: Turla Samples from RUAG Cyber Attack
*/

/* Rule Set ----------------------------------------------------------------- */

rule Turla_APT_srsvc {
	meta:
		description = "Detects Turla malware (based on sample used in the RUAG APT case)"
		author = "Florian Roth"
		family = "Turla"
		reference = "https://www.govcert.admin.ch/blog/22/technical-report-about-the-ruag-espionage-case"
		date = "2016-06-09"
		hash1 = "65996f266166dbb479a42a15a236e6564f0b322d5d68ee546244d7740a21b8f7"
		hash2 = "25c7ff1eb16984a741948f2ec675ab122869b6edea3691b01d69842a53aa3bac"
	strings:
		$x1 = "SVCHostServiceDll.dll" fullword ascii

		$s2 = "msimghlp.dll" fullword wide
		$s3 = "srservice" fullword wide
		$s4 = "ModStart" fullword ascii
		$s5 = "ModStop" fullword ascii
	condition:
		( uint16(0) == 0x5a4d and filesize < 20KB and ( 1 of ($x*) or all of ($s*) ) )
		or ( all of them )
}

rule Turla_APT_Malware_Gen1 {
	meta:
		description = "Detects Turla malware (based on sample used in the RUAG APT case)"
		author = "Florian Roth"
		family = "Turla"
		reference = "https://www.govcert.admin.ch/blog/22/technical-report-about-the-ruag-espionage-case"
		date = "2016-06-09"
		hash1 = "0e1bf347c37fb199886f1e675e372ba55ac4627e8be2f05a76c2c64f9b6ed0e4"
		hash2 = "7206075cd8f1004e8f1f759d46e98bfad4098b8642412811a214c0155a1f08b9"
		hash3 = "fe3ffd7438c0d38484bf02a78a19ea81a6f51b4b3f2b2228bd21974c2538bbcd"
		hash4 = "c49111af049dd9746c6b1980db6e150b2a79ca1569b23ed2cba81c85c00d82b4"
		hash5 = "b62a643c96e2e41f639d2a8ce11d61e6b9d7fb3a9baf011120b7fec1b4ee3cf4"
		hash6 = "edb12790b5cd959bc2e53a4b369a4fd747153e6c9d50f6a69ff047f7857a4348"
		hash7 = "8f2ea0f916fda1dfb771f5441e919c561da5b6334b9f2fffcbf53db14063b24a"
		hash8 = "8dddc744bbfcf215346c812aa569e49523996f73a1f22fe4e688084ce1225b98"
		hash9 = "0c69258adcc97632b729e55664c22cd942812336d41e8ea0cff9ddcafaded20f"
		hash10 = "2b4fba1ef06f85d1395945db40a9f2c3b3ed81b56fb9c2d5e5bb693c230215e2"
	strings:
		$x1 = "too long data for this type of transport" fullword ascii
		$x2 = "not enough server resources to complete operation" fullword ascii
		$x3 = "Task not execute. Arg file failed." fullword ascii
		$x4 = "Global\\MSCTF.Shared.MUTEX.ZRX" fullword ascii

		$s1 = "peer has closed the connection" fullword ascii
		$s2 = "tcpdump.exe" fullword ascii
		$s3 = "windump.exe" fullword ascii
		$s4 = "dsniff.exe" fullword ascii
		$s5 = "wireshark.exe" fullword ascii
		$s6 = "ethereal.exe" fullword ascii
		$s7 = "snoop.exe" fullword ascii
		$s8 = "ettercap.exe" fullword ascii
		$s9 = "miniport.dat" fullword ascii
		$s10 = "net_password=%s" fullword ascii
	condition:
		( uint16(0) == 0x5a4d and filesize < 2000KB and ( 2 of ($x*) or 8 of ($s*) ) )
		or ( 12 of them )
}

rule Turla_APT_Malware_Gen2 {
	meta:
		description = "Detects Turla malware (based on sample used in the RUAG APT case)"
		author = "Florian Roth"
		family = "Turla"
		reference = "https://www.govcert.admin.ch/blog/22/technical-report-about-the-ruag-espionage-case"
		date = "2016-06-09"
		hash1 = "0e1bf347c37fb199886f1e675e372ba55ac4627e8be2f05a76c2c64f9b6ed0e4"
		hash2 = "7206075cd8f1004e8f1f759d46e98bfad4098b8642412811a214c0155a1f08b9"
		hash3 = "fe3ffd7438c0d38484bf02a78a19ea81a6f51b4b3f2b2228bd21974c2538bbcd"
		hash4 = "c49111af049dd9746c6b1980db6e150b2a79ca1569b23ed2cba81c85c00d82b4"
	strings:
		$x1 = "Internal command not support =((" fullword ascii
		$x2 = "L|-1|AS_CUR_USER:OpenProcessToken():%d, %s|" fullword ascii
		$x3 = "L|-1|CreateProcessAsUser():%d, %s|" fullword ascii
		$x4 = "AS_CUR_USER:OpenProcessToken():%d" fullword ascii
		$x5 = "L|-1|AS_CUR_USER:LogonUser():%d, %s|" fullword ascii
		$x6 = "L|-1|try to run dll %s with user priv|" fullword ascii
		$x7 = "\\\\.\\Global\\PIPE\\sdlrpc" fullword ascii
		$x8 = "\\\\%s\\pipe\\comnode" fullword ascii
		$x9 = "Plugin dll stop failed." fullword ascii
		$x10 = "AS_USER:LogonUser():%d" fullword ascii

		$s1 = "MSIMGHLP.DLL" fullword wide
		$s2 = "msimghlp.dll" fullword ascii
		$s3 = "ximarsh.dll" fullword ascii
		$s4 = "msximl.dll" fullword ascii
		$s5 = "INTERNAL.dll" fullword ascii
		$s6 = "\\\\.\\Global\\PIPE\\" fullword ascii
		$s7 = "ieuser.exe" fullword ascii
	condition:
		( uint16(0) == 0x5a4d and filesize < 2000KB and ( 1 of ($x*) or 5 of ($s*) ) )
		or ( 10 of them )
}

rule Turla_APT_Malware_Gen3 {
	meta:
		description = "Detects Turla malware (based on sample used in the RUAG APT case)"
		author = "Florian Roth"
		family = "Turla"
		reference = "https://www.govcert.admin.ch/blog/22/technical-report-about-the-ruag-espionage-case"
		date = "2016-06-09"
		hash1 = "c49111af049dd9746c6b1980db6e150b2a79ca1569b23ed2cba81c85c00d82b4"
		hash2 = "b62a643c96e2e41f639d2a8ce11d61e6b9d7fb3a9baf011120b7fec1b4ee3cf4"
		hash3 = "edb12790b5cd959bc2e53a4b369a4fd747153e6c9d50f6a69ff047f7857a4348"
		hash4 = "8f2ea0f916fda1dfb771f5441e919c561da5b6334b9f2fffcbf53db14063b24a"
		hash5 = "8dddc744bbfcf215346c812aa569e49523996f73a1f22fe4e688084ce1225b98"
		hash6 = "0c69258adcc97632b729e55664c22cd942812336d41e8ea0cff9ddcafaded20f"
		hash7 = "2b4fba1ef06f85d1395945db40a9f2c3b3ed81b56fb9c2d5e5bb693c230215e2"
		hash8 = "7206075cd8f1004e8f1f759d46e98bfad4098b8642412811a214c0155a1f08b9"
		hash9 = "edb12790b5cd959bc2e53a4b369a4fd747153e6c9d50f6a69ff047f7857a4348"
	strings:
		$x1 = "\\\\.\\pipe\\sdlrpc" fullword ascii
		$x2 = "WaitMutex Abandoned %p" fullword ascii
		$x3 = "OPER|Wrong config: no port|" fullword ascii
		$x4 = "OPER|Wrong config: no lastconnect|" fullword ascii
		$x5 = "OPER|Wrong config: empty address|" fullword ascii
		$x6 = "Trans task %d obj %s ACTIVE fail robj %s" fullword ascii
		$x7 = "OPER|Wrong config: no auth|" fullword ascii
		$x8 = "OPER|Sniffer '%s' running... ooopppsss...|" fullword ascii

		$s1 = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\5.0\\User Agent\\Post Platform" fullword ascii
		$s2 = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Internet Settings\\5.0\\User Agent\\Pre Platform" fullword ascii
		$s3 = "www.yahoo.com" fullword ascii
		$s4 = "MSXIML.DLL" fullword wide
		$s5 = "www.bing.com" fullword ascii
		$s6 = "%s: http://%s%s" fullword ascii
		$s7 = "/javascript/view.php" fullword ascii
		$s8 = "Task %d failed %s,%d" fullword ascii
		$s9 = "Mozilla/4.0 (compatible; MSIE %d.0; " fullword ascii
	condition:
		( uint16(0) == 0x5a4d and filesize < 2000KB and ( 1 of ($x*) or 6 of ($s*) ) )
		or ( 10 of them )
}
