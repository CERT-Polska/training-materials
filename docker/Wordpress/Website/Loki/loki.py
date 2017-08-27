# -*- coding: utf-8 -*-

"""
Loki
Simple IOC Scanner

Detection is based on three detection methods:

1. File Name IOC
   Applied to file names

2. Yara Check
   Applied to files and processes

3. Hash Check
   Compares known malicious hashes with th ones of the scanned files

Loki combines all IOCs from ReginScanner and SkeletonKeyScanner and is the
little brother of THOR our full-featured corporate APT Scanner

Florian Roth
BSK Consulting GmbH

DISCLAIMER - USE AT YOUR OWN RISK.
"""

import sys
import os
import argparse
import traceback
import yara         # install 'yara-python' module not the outdated 'yara' module
import re
import stat
import psutil
import signal as signal_module
from sys import platform as _platform
from subprocess import Popen, PIPE
from collections import Counter

# LOKI Modules
from lib.lokilogger import *

sys.stdout = codecs.getwriter('utf8')(sys.stdout)

from lib.helpers import *
from lib.doublepulsar import DoublePulsar

# Platform
platform = ""
if _platform == "linux" or _platform == "linux2":
    platform = "linux"
elif _platform == "darwin":
    platform = "osx"
elif _platform == "win32":
    platform = "windows"

# Win32 Imports
if platform == "windows":
    try:
        import wmi
        import win32api
        from win32com.shell import shell
    except Exception, e:
        print "Linux System - deactivating process memory check ..."
        platform = "linux" # crazy guess

if platform == "":
    print "Unable to determine platform - LOKI is lost."
    sys.exit(1)

# Predefined Evil Extensions
EVIL_EXTENSIONS = [".vbs", ".ps", ".ps1", ".rar", ".tmp", ".bas", ".bat", ".chm", ".cmd", ".com", ".cpl",
                   ".crt", ".dll", ".exe", ".hta", ".js", ".lnk", ".msc", ".ocx", ".pcd", ".pif", ".pot", ".pdf",
                   ".reg", ".scr", ".sct", ".sys", ".url", ".vb", ".vbe", ".wsc", ".wsf", ".wsh", ".ct", ".t",
                   ".input", ".war", ".jsp", ".php", ".asp", ".aspx", ".doc", ".docx", ".pdf", ".xls", ".xlsx", ".ppt",
                   ".pptx", ".tmp", ".log", ".dump", ".pwd", ".w", ".txt", ".conf", ".cfg", ".conf", ".config", ".psd1",
                   ".psm1", ".ps1xml", ".clixml", ".psc1", ".pssc", ".pl", ".www", ".rdp", ".jar", ".docm"]

SCRIPT_EXTENSIONS = [".asp", ".vbs", ".ps1", ".bas", ".bat", ".js", ".vb", ".vbe", ".vbs", ".wsc", ".wsf",
                     ".wsh",  ".jsp", ".php", ".asp", ".aspx", ".psd1", ".psm1", ".ps1xml", ".clixml", ".psc1",
                     ".pssc"]

SCRIPT_TYPES = ["VBS", "PHP", "JSP", "ASP", "BATCH"]

class Loki():

    # Signatures
    yara_rules = []
    filename_iocs = []
    hashes_md5 = {}
    hashes_sha1 = {}
    hashes_sha256 = {}
    false_hashes = {}
    c2_server = {}

    # Yara rule directories
    yara_rule_directories = []

    # Excludes (list of regex that match within the whole path) (user-defined via excluces.cfg)
    fullExcludes = []
    # Platform specific excludes (match the beginning of the full path) (not user-defined)
    startExcludes = []

    # File type magics
    filetype_magics = {}
    max_filetype_magics = 0

    # Predefined paths to skip (Linux platform)
    LINUX_PATH_SKIPS_START = set(["/proc", "/dev", "/media", "/sys/kernel/debug", "/sys/kernel/slab", "/sys/devices", "/usr/src/linux" ])
    LINUX_PATH_SKIPS_END = set(["/initctl"])

    def __init__(self, intense_mode):

        # Scan Mode
        self.intense_mode = intense_mode

        # Get application path
        self.app_path = get_application_path()

        # Check if signature database is present
        sig_dir = os.path.join(self.app_path, "./signature-base/")
        if not os.path.exists(sig_dir) or os.listdir(sig_dir) == []:
            logger.log("NOTICE", "The 'signature-base' subdirectory doesn't exist or is empty. "
                                  "Trying to retrieve the signature database automatically.")
            updateLoki(sigsOnly=True)

        # Excludes
        self.initialize_excludes(os.path.join(self.app_path, "./config/excludes.cfg"))

        # Linux excludes from mtab
        if platform == "linux":
            self.startExcludes = self.LINUX_PATH_SKIPS_START | set(getExcludedMountpoints())
        # OSX excludes like Linux until we get some field data
        if platform == "osx":
            self.startExcludes = self.LINUX_PATH_SKIPS_START

        # Set IOC path
        self.ioc_path = os.path.join(self.app_path, "./signature-base/iocs/")

        # Yara rule directories
        self.yara_rule_directories.append(os.path.join(self.app_path, "./signature-base/yara"))
        self.yara_rule_directories.append(os.path.join(self.app_path, "./signature-base/iocs/yara"))

        # Read IOCs -------------------------------------------------------
        # File Name IOCs (all files in iocs that contain 'filename')
        self.initialize_filename_iocs(self.ioc_path)
        logger.log("INFO","File Name Characteristics initialized with %s regex patterns" % len(self.filename_iocs))

        # C2 based IOCs (all files in iocs that contain 'c2')
        self.initialize_c2_iocs(self.ioc_path)
        logger.log("INFO","C2 server indicators initialized with %s elements" % len(self.c2_server.keys()))

        # Hash based IOCs (all files in iocs that contain 'hash')
        self.initialize_hash_iocs(self.ioc_path)
        logger.log("INFO","Malicious MD5 Hashes initialized with %s hashes" % len(self.hashes_md5.keys()))
        logger.log("INFO","Malicious SHA1 Hashes initialized with %s hashes" % len(self.hashes_sha1.keys()))
        logger.log("INFO","Malicious SHA256 Hashes initialized with %s hashes" % len(self.hashes_sha256.keys()))

        # Hash based False Positives (all files in iocs that contain 'hash' and 'falsepositive')
        self.initialize_hash_iocs(self.ioc_path, false_positive=True)
        logger.log("INFO","False Positive Hashes initialized with %s hashes" % len(self.false_hashes.keys()))

        # Compile Yara Rules
        self.initialize_yara_rules()

        # Initialize File Type Magic signatures
        self.initialize_filetype_magics(os.path.join(self.app_path, './signature-base/misc/file-type-signatures.txt'))

    def scan_path(self, path):

        # Startup
        logger.log("INFO","Scanning %s ...  " % path)

        # Counter
        c = 0

        for root, directories, files in os.walk(path, onerror=walk_error, followlinks=False):

            # Skip paths that start with ..
            newDirectories = []
            for dir in directories:
                skipIt = False

                # Generate a complete path for comparisons
                completePath = os.path.join(root, dir).lower() + os.sep

                # Platform specific excludes
                for skip in self.startExcludes:
                    if completePath.startswith(skip):
                        logger.log("INFO", "Skipping %s directory" % skip)
                        skipIt = True

                if not skipIt:
                    newDirectories.append(dir)
            directories[:] = newDirectories

            # Loop through files
            for filename in files:
                try:
                    # Findings
                    reasons = []
                    # Total Score
                    total_score = 0

                    # Get the file and path
                    filePath = os.path.join(root,filename)
                    # Clean the values for YARA matching
                    # > due to errors when Unicode characters are passed to the match function as
                    #   external variables
                    filePathCleaned = filePath.encode('ascii', errors='replace')
                    fileNameCleaned = filename.encode('ascii', errors='replace')

                    # Get Extension
                    extension = os.path.splitext(filePath)[1].lower()

                    # Skip marker
                    skipIt = False

                    # Unicode error test
                    #if 1 > 0:
                    #    walk_error(OSError("[Error 3] No such file or directory"))

                    # User defined excludes
                    for skip in self.fullExcludes:
                        if skip.search(filePath):
                            logger.log("DEBUG", "Skipping element %s" % filePath)
                            skipIt = True

                    # Linux directory skip
                    if platform == "linux" or platform == "osx":

                        # Skip paths that end with ..
                        for skip in self.LINUX_PATH_SKIPS_END:
                            if filePath.endswith(skip):
                                if self.LINUX_PATH_SKIPS_END[skip] == 0:
                                    logger.log("INFO", "Skipping %s element" % skip)
                                    self.LINUX_PATH_SKIPS_END[skip] = 1
                                    skipIt = True

                        # File mode
                        mode = os.stat(filePath).st_mode
                        if stat.S_ISCHR(mode) or stat.S_ISBLK(mode) or stat.S_ISFIFO(mode) or stat.S_ISLNK(mode) or stat.S_ISSOCK(mode):
                            continue

                    # Skip
                    if skipIt:
                        continue

                    # Counter
                    c += 1

                    if not args.noindicator:
                        printProgress(c)

                    # Skip program directory
                    # print appPath.lower() +" - "+ filePath.lower()
                    if self.app_path.lower() in filePath.lower():
                        logger.log("DEBUG", "Skipping file in program directory FILE: %s" % filePathCleaned)
                        continue

                    fileSize = os.stat(filePath).st_size
                    # print file_size

                    # File Name Checks -------------------------------------------------
                    for fioc in self.filename_iocs:
                        match = fioc['regex'].search(filePath)
                        if match:
                            # Check for False Positive
                            if fioc['regex_fp']:
                                match_fp = fioc['regex_fp'].search(filePath)
                                if match_fp:
                                    continue
                            # Create Reason
                            reasons.append("File Name IOC matched PATTERN: %s SUBSCORE: %s DESC: %s" % (fioc['regex'].pattern, fioc['score'], fioc['description']))
                            total_score += int(fioc['score'])

                    # Access check (also used for magic header detection)
                    firstBytes = ""
                    firstBytesString = "-"
                    hashString = ""
                    try:
                        with open(filePath, 'rb') as f:
                            firstBytes = f.read(4)
                    except Exception, e:
                        logger.log("DEBUG", "Cannot open file %s (access denied)" % filePathCleaned)

                    # Evaluate Type
                    fileType = get_file_type(filePath, self.filetype_magics, self.max_filetype_magics, logger)

                    # Fast Scan Mode - non intense
                    do_intense_check = True
                    if not self.intense_mode and fileType == "UNKNOWN" and extension not in EVIL_EXTENSIONS:
                        if args.printAll:
                            logger.log("INFO", "Skipping file due to fast scan mode: %s" % filePathCleaned)
                        do_intense_check = False

                    # Set fileData to an empty value
                    fileData = ""

                    # Evaluations -------------------------------------------------------
                    # Evaluate size
                    if fileSize > (args.s * 1024):
                        # Print files
                        do_intense_check = False

                    # Some file types will force intense check
                    if fileType == "MDMP":
                        do_intense_check = True

                    # Intense Check switch
                    if do_intense_check:
                        if args.printAll:
                            logger.log("INFO", "Scanning %s TYPE: %s SIZE: %s" % (filePathCleaned, fileType, fileSize))
                    else:
                        if args.printAll:
                            logger.log("INFO", "Checking %s TYPE: %s SIZE: %s" % (filePathCleaned, fileType, fileSize))

                    # Hash Check -------------------------------------------------------
                    # Do the check
                    if do_intense_check:

                        fileData = self.get_file_data(filePath)

                        # First bytes
                        firstBytesString = "%s / %s" % (fileData[:20].encode('hex'), removeNonAsciiDrop(fileData[:20]) )

                        # Hash Eval
                        matchType = None
                        matchDesc = None
                        matchHash = None
                        md5 = "-"
                        sha1 = "-"
                        sha256 = "-"

                        md5, sha1, sha256 = generateHashes(fileData)

                        # False Positive Hash
                        if md5 in self.false_hashes.keys() or sha1 in self.false_hashes.keys() or sha256 in self.false_hashes.keys():
                            continue

                        # Malware Hash
                        if md5 in self.hashes_md5.keys():
                            matchType = "MD5"
                            matchDesc = self.hashes_md5[md5]
                            matchHash = md5
                        elif sha1 in self.hashes_sha1.keys():
                            matchType = "SHA1"
                            matchDesc = self.hashes_sha1[sha1]
                            matchHash = sha1
                        elif sha256 in self.hashes_sha256.keys():
                            matchType = "SHA256"
                            matchDesc = self.hashes_sha256[sha256]
                            matchHash = sha256

                        # Hash string
                        hashString = "MD5: %s SHA1: %s SHA256: %s" % ( md5, sha1, sha256 )

                        if matchType:
                            reasons.append("Malware Hash TYPE: %s HASH: %s SUBSCORE: 100 DESC: %s" % (
                            matchType, matchHash, matchDesc))
                            total_score += 100

                        # Regin .EVT FS Check
                        if len(fileData) > 11 and args.reginfs:

                            # Check if file is Regin virtual .evt file system
                            self.scan_regin_fs(fileData, filePath)

                        # Script Anomalies Check
                        if args.scriptanalysis:
                            if extension in SCRIPT_EXTENSIONS or type in SCRIPT_TYPES:
                                logger.log("DEBUG", "Performing character analysis on file %s ... " % filePath)
                                message, score = self.script_stats_analysis(fileData)
                                if message:
                                    reasons.append("%s SCORE: %s" % (message, score))
                                    total_score += score

                        # Yara Check -------------------------------------------------------

                        # Memory Dump Scan
                        if fileType == "MDMP":
                            logger.log("INFO", "Scanning memory dump file %s" % filePathCleaned)

                        # Umcompressed SWF scan
                        if fileType == "ZWS" or fileType == "CWS":
                            logger.log("INFO", "Scanning decompressed SWF file %s" % filePathCleaned)
                            success, decompressedData = decompressSWFData(fileData)
                            if success:
                               fileData = decompressedData

                        # Scan the read data
                        try:
                            for (score, rule, description, matched_strings) in \
                                    self.scan_data(fileData=fileData,
                                                   fileType=fileType,
                                                   fileName=fileNameCleaned,
                                                   filePath=filePathCleaned,
                                                   extension=extension,
                                                   md5=md5  # legacy rule support
                                                   ):
                                # Message
                                message = "Yara Rule MATCH: %s SUBSCORE: %s DESCRIPTION: %s" % (rule, score, description)
                                # Matches
                                if matched_strings:
                                    message += " MATCHES: %s" % matched_strings

                                total_score += score
                                reasons.append(message)

                        except Exception, e:
                            logger.log("ERROR", "Cannot YARA scan file: %s" % filePathCleaned)

                    # Info Line -----------------------------------------------------------------------
                    fileInfo = "FILE: %s SCORE: %s TYPE: %s SIZE: %s FIRST_BYTES: %s %s %s " % (
                        filePath, total_score, fileType, fileSize, firstBytesString, hashString, getAgeString(filePath))

                    # Now print the total result
                    if total_score >= args.a:
                        message_type = "ALERT"
                    elif total_score >= args.w:
                        message_type = "WARNING"
                    elif total_score >= args.n:
                        message_type = "NOTICE"

                    if total_score < args.n:
                        continue

                    # Reasons to message body
                    message_body = fileInfo
                    for i, r in enumerate(reasons):
                        if i < 2 or args.allreasons:
                            message_body += "REASON_{0}: {1}".format(i+1, r.encode('ascii', errors='replace'))

                    logger.log(message_type, message_body)

                except Exception, e:
                    if logger.debug:
                        traceback.print_exc()
                        sys.exit(1)

    def scan_data(self, fileData, fileType="-", fileName="-", filePath="-", extension="-", md5="-"):

        # Scan parameters
        #print fileType, fileName, filePath, extension, md5
        # Scan with yara
        try:
            for rules in self.yara_rules:

                # Yara Rule Match
                matches = rules.match(data=fileData,
                                      externals={
                                          'filename': fileName,
                                          'filepath': filePath,
                                          'extension': extension,
                                          'filetype': fileType,
                                          'md5': md5
                                      })

                # If matched
                if matches:
                    for match in matches:

                        score = 70
                        description = "not set"

                        # Built-in rules have meta fields (cannot be expected from custom rules)
                        if hasattr(match, 'meta'):

                            if 'description' in match.meta:
                                description = match.meta['description']

                            # If a score is given
                            if 'score' in match.meta:
                                score = int(match.meta['score'])

                        # Matching strings
                        matched_strings = ""
                        if hasattr(match, 'strings'):
                            # Get matching strings
                            matched_strings = self.get_string_matches(match.strings)

                        yield score, match.rule, description, matched_strings

        except Exception, e:
            if logger.debug:
                traceback.print_exc()

    def get_string_matches(self, strings):
        try:
            string_matches = []
            matching_strings = ""
            for string in strings:
                # print string
                extract = string[2]
                if not extract in string_matches:
                    string_matches.append(extract)

            string_num = 1
            for string in string_matches:
                matching_strings += " Str" + str(string_num) + ": " + removeNonAscii(removeBinaryZero(string))
                string_num += 1

            # Limit string
            if len(matching_strings) > 140:
                matching_strings = matching_strings[:140] + " ... (truncated)"

            return matching_strings.lstrip(" ")
        except:
            traceback.print_exc()

    def check_svchost_owner(self, owner):
        ## Locale setting
        import ctypes
        import locale
        windll = ctypes.windll.kernel32
        locale = locale.windows_locale[ windll.GetUserDefaultUILanguage() ]
        if locale == 'fr_FR':
            return (owner.upper().startswith("SERVICE LOCAL") or
                owner.upper().startswith(u"SERVICE RÉSEAU") or
                re.match(r"SERVICE R.SEAU", owner) or
                owner == u"Système"  or
                owner.upper().startswith(u"AUTORITE NT\Système") or
                re.match(r"AUTORITE NT\\Syst.me", owner))
        elif locale == 'ru_RU':
            return (owner.upper().startswith("NET") or
                owner == u"система" or
                owner.upper().startswith("LO"))
        else:
            return ( owner.upper().startswith("NT ") or owner.upper().startswith("NET") or
                owner.upper().startswith("LO") or
                owner.upper().startswith("SYSTEM"))


    def scan_processes(self):
        # WMI Handler
        c = wmi.WMI()
        processes = c.Win32_Process()
        t_systemroot = os.environ['SYSTEMROOT']

        # WinInit PID
        wininit_pid = 0
        # LSASS Counter
        lsass_count = 0

        for process in processes:

            try:

                # Gather Process Information --------------------------------------
                pid = process.ProcessId
                name = process.Name
                cmd = process.CommandLine
                if not cmd:
                    cmd = "N/A"
                if not name:
                    name = "N/A"
                path = "none"
                parent_pid = process.ParentProcessId
                priority = process.Priority
                ws_size = process.VirtualSize
                if process.ExecutablePath:
                    path = process.ExecutablePath
                # Owner
                try:
                    owner_raw = process.GetOwner()
                    owner = owner_raw[2]
                except Exception, e:
                    owner = "unknown"
                if not owner:
                    owner = "unknown"

            except Exception, e:
                logger.log("ALERT", "Error getting all process information. Did you run the scanner 'As Administrator'?")
                continue

            # Is parent to other processes - save PID
            if name == "wininit.exe":
                wininit_pid = pid

            # Skip some PIDs ------------------------------------------------------
            if pid == 0 or pid == 4:
                logger.log("INFO", "Skipping Process PID: %s NAME: %s CMD: %s" % ( pid, name, cmd ))
                continue

            # Skip own process ----------------------------------------------------
            if os.getpid() == pid:
                logger.log("INFO", "Skipping LOKI Process PID: %s NAME: %s CMD: %s" % ( pid, name, cmd ))
                continue

            # Print info ----------------------------------------------------------
            logger.log("INFO", "Scanning Process PID: %s NAME: %s CMD: %s" % ( pid, name, cmd ))

            # Special Checks ------------------------------------------------------
            # better executable path
            if not "\\" in cmd and path != "none":
                cmd = path

            # Skeleton Key Malware Process
            if re.search(r'psexec .* [a-fA-F0-9]{32}', cmd, re.IGNORECASE):
                logger.log("WARNING", "Process that looks liks SKELETON KEY psexec execution detected PID: %s NAME: %s CMD: %s" % ( pid, name, cmd))

            # File Name Checks -------------------------------------------------
            for fioc in self.filename_iocs:
                match = fioc['regex'].search(cmd)
                if match:
                    if fioc['score'] > 70:
                        logger.log("ALERT", "File Name IOC matched PATTERN: %s DESC: %s MATCH: %s" % (fioc['regex'].pattern, fioc['description'], cmd))
                    elif fioc['score'] > 40:
                        logger.log("WARNING", "File Name Suspicious IOC matched PATTERN: %s DESC: %s MATCH: %s" % (fioc['regex'].pattern, fioc['description'], cmd))

            # Special Checks ---------------------------------------------------
            # Suspicious waitfor - possible backdoor https://twitter.com/subTee/status/872274262769500160
            if name == "waitfor.exe":
                logger.log("WARNING", "Suspicious waitfor.exe process https://twitter.com/subTee/status/872274262769500160 PID: %s NAME: %s CMD: %s" % ( pid, name, cmd ))

            # Yara rule match
            # only on processes with a small working set size
            if int(ws_size) < ( 100 * 1048576 ): # 100 MB
                try:
                    alerts = []
                    for rules in self.yara_rules:
                        # continue - fast switch
                        matches = rules.match(pid=pid)
                        if matches:
                            for match in matches:

                                # Preset memory_rule
                                memory_rule = 1

                                # Built-in rules have meta fields (cannot be expected from custom rules)
                                if hasattr(match, 'meta'):

                                    # If a score is given
                                    if 'memory' in match.meta:
                                        memory_rule = int(match.meta['memory'])

                                # If rule is meant to be applied to process memory as well
                                if memory_rule == 1:

                                    # print match.rule
                                    alerts.append("Yara Rule MATCH: %s PID: %s NAME: %s CMD: %s" % ( match.rule, pid, name, cmd))

                    if len(alerts) > 3:
                        logger.log("INFO", "Too many matches on process memory - most likely a false positive PID: %s NAME: %s CMD: %s" % (pid, name, cmd))
                    elif len(alerts) > 0:
                        for alert in alerts:
                            logger.log("ALERT", alert)
                except Exception, e:
                    if logger.debug:
                        traceback.print_exc()
                    logger.log("ERROR", "Error while process memory Yara check (maybe the process doesn't exist anymore or access denied). PID: %s NAME: %s" % ( pid, name))
            else:
                logger.log("DEBUG", "Skipped Yara memory check due to the process' big working set size (stability issues) PID: %s NAME: %s SIZE: %s" % ( pid, name, ws_size))

            ###############################################################
            # THOR Process Connection Checks
            self.check_process_connections(process)

            ###############################################################
            # THOR Process Anomaly Checks
            # Source: Sysforensics http://goo.gl/P99QZQ

            # Process: System
            if name == "System" and not pid == 4:
                logger.log("WARNING", "System process without PID=4 PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                    str(pid), name, owner, cmd, path))

            # Process: smss.exe
            if name == "smss.exe" and not parent_pid == 4:
                logger.log("WARNING", "smss.exe parent PID is != 4 PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                    str(pid), name, owner, cmd, path))
            if path != "none":
                if name == "smss.exe" and not ( "system32" in path.lower() or "system32" in cmd.lower() ):
                    logger.log("WARNING", "smss.exe path is not System32 PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                        str(pid), name, owner, cmd, path))
            if name == "smss.exe" and priority is not 11:
                logger.log("WARNING", "smss.exe priority is not 11 PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                    str(pid), name, owner, cmd, path))

            # Process: csrss.exe
            if path != "none":
                if name == "csrss.exe" and not ( "system32" in path.lower() or "system32" in cmd.lower() ):
                    logger.log("WARNING", "csrss.exe path is not System32 PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                        str(pid), name, owner, cmd, path))
            if name == "csrss.exe" and priority is not 13:
                logger.log("WARNING", "csrss.exe priority is not 13 PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                    str(pid), name, owner, cmd, path))

            # Process: wininit.exe
            if path != "none":
                if name == "wininit.exe" and not ( "system32" in path.lower() or "system32" in cmd.lower() ):
                    logger.log("WARNING", "wininit.exe path is not System32 PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                        str(pid), name, owner, cmd, path))
            if name == "wininit.exe" and priority is not 13:
                logger.log("NOTICE", "wininit.exe priority is not 13 PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                    str(pid), name, owner, cmd, path))
            # Is parent to other processes - save PID
            if name == "wininit.exe":
                wininit_pid = pid

            # Process: services.exe
            if path != "none":
                if name == "services.exe" and not ( "system32" in path.lower() or "system32" in cmd.lower() ):
                    logger.log("WARNING", "services.exe path is not System32 PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                        str(pid), name, owner, cmd, path))
            if name == "services.exe" and priority is not 9:
                logger.log("WARNING", "services.exe priority is not 9 PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                    str(pid), name, owner, cmd, path))
            if wininit_pid > 0:
                if name == "services.exe" and not parent_pid == wininit_pid:
                    logger.log("WARNING", "services.exe parent PID is not the one of wininit.exe PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                        str(pid), name, owner, cmd, path))

            # Process: lsass.exe
            if path != "none":
                if name == "lsass.exe" and not ( "system32" in path.lower() or "system32" in cmd.lower() ):
                    logger.log("WARNING", "lsass.exe path is not System32 PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                        str(pid), name, owner, cmd, path))
            if name == "lsass.exe" and priority is not 9:
                logger.log("WARNING", "lsass.exe priority is not 9 PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                    str(pid), name, owner, cmd, path))
            if wininit_pid > 0:
                if name == "lsass.exe" and not parent_pid == wininit_pid:
                    logger.log("WARNING", "lsass.exe parent PID is not the one of wininit.exe PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                        str(pid), name, owner, cmd, path))
            # Only a single lsass process is valid - count occurrences
            if name == "lsass.exe":
                lsass_count += 1
                if lsass_count > 1:
                    logger.log("WARNING", "lsass.exe count is higher than 1 PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                        str(pid), name, owner, cmd, path))

            # Process: svchost.exe
            if path is not "none":
                if name == "svchost.exe" and not ( "system32" in path.lower() or "system32" in cmd.lower() ):
                    logger.log("WARNING", "svchost.exe path is not System32 PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                        str(pid), name, owner, cmd, path))
            if name == "svchost.exe" and priority is not 8:
                logger.log("NOTICE", "svchost.exe priority is not 8 PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                    str(pid), name, owner, cmd, path))
            if name == "svchost.exe" and not ( self.check_svchost_owner(owner) or "UnistackSvcGroup" in cmd):
                logger.log("WARNING", "svchost.exe process owner is suspicious PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                    str(pid), name, owner, cmd, path))

            if name == "svchost.exe" and not " -k " in cmd and cmd != "N/A":
                logger.log("WARNING", "svchost.exe process does not contain a -k in its command line PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                    str(pid), name, owner, cmd, path))

            # Process: lsm.exe
            if path != "none":
                if name == "lsm.exe" and not ( "system32" in path.lower() or "system32" in cmd.lower() ):
                    logger.log("WARNING", "lsm.exe path is not System32 PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                        str(pid), name, owner, cmd, path))
            if name == "lsm.exe" and priority is not 8:
                logger.log("NOTICE", "lsm.exe priority is not 8 PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                    str(pid), name, owner, cmd, path))
            if name == "lsm.exe" and not ( owner.startswith("NT ") or owner.startswith("LO") or owner.startswith("SYSTEM")  or owner.startswith(u"система")):
                logger.log(u"WARNING", "lsm.exe process owner is suspicious PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                    str(pid), name, owner, cmd, path))
            if wininit_pid > 0:
                if name == "lsm.exe" and not parent_pid == wininit_pid:
                    logger.log("WARNING", "lsm.exe parent PID is not the one of wininit.exe PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                        str(pid), name, owner, cmd, path))

            # Process: winlogon.exe
            if name == "winlogon.exe" and priority is not 13:
                logger.log("WARNING", "winlogon.exe priority is not 13 PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                    str(pid), name, owner, cmd, path))
            if re.search("(Windows 7|Windows Vista)", getPlatformFull()):
                if name == "winlogon.exe" and parent_pid > 0:
                    for proc in processes:
                        if parent_pid == proc.ProcessId:
                            logger.log("WARNING", "winlogon.exe has a parent ID but should have none PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s PARENTPID: %s" % (
                                str(pid), name, owner, cmd, path, str(parent_pid)))

            # Process: explorer.exe
            if path != "none":
                if name == "explorer.exe" and not t_systemroot.lower() in path.lower():
                    logger.log("WARNING", "explorer.exe path is not %%SYSTEMROOT%% PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                        str(pid), name, owner, cmd, path))
            if name == "explorer.exe" and parent_pid > 0:
                for proc in processes:
                    if parent_pid == proc.ProcessId:
                        logger.log("NOTICE", "explorer.exe has a parent ID but should have none PID: %s NAME: %s OWNER: %s CMD: %s PATH: %s" % (
                            str(pid), name, owner, cmd, path))

    def check_process_connections(self, process):
        try:

            # Limits
            MAXIMUM_CONNECTIONS = 20

            # Counter
            connection_count = 0

            # Pid from process
            pid = process.ProcessId
            name = process.Name

            # Get psutil info about the process
            p = psutil.Process(pid)

            # print "Checking connections of %s" % process.Name
            for x in p.connections():

                # Evaluate a usable command line to check
                try:
                    command = process.CommandLine
                except Exception:
                    command = p.cmdline()

                if x.status == 'LISTEN':
                    connection_count += 1
                    logger.log("NOTICE","Listening process PID: %s NAME: %s COMMAND: %s IP: %s PORT: %s" % (
                        str(pid), name, command, str(x.laddr[0]), str(x.laddr[1]) ))
                    if str(x.laddr[1]) == "0":
                        logger.log("WARNING",
                            "Listening on Port 0 PID: %s NAME: %s COMMAND: %s  IP: %s PORT: %s" % (
                                str(pid), name, command, str(x.laddr[0]), str(x.laddr[1]) ))

                if x.status == 'ESTABLISHED':

                    # Lookup Remote IP
                    # Geo IP Lookup removed

                    # Check keyword in remote address
                    is_match, description = self.check_c2(str(x.raddr[0]))
                    if is_match:
                        logger.log("ALERT",
                            "Malware Domain/IP match in remote address PID: %s NAME: %s COMMAND: %s IP: %s PORT: %s DESC: %s" % (
                                str(pid), name, command, str(x.raddr[0]), str(x.raddr[1]), description))

                    # Full list
                    connection_count += 1
                    logger.log("NOTICE", "Established connection PID: %s NAME: %s COMMAND: %s LIP: %s LPORT: %s RIP: %s RPORT: %s" % (
                        str(pid), name, command, str(x.laddr[0]), str(x.laddr[1]), str(x.raddr[0]), str(x.raddr[1]) ))

                # Maximum connection output
                if connection_count > MAXIMUM_CONNECTIONS:
                    logger.log("NOTICE", "Connection output threshold reached. Output truncated.")
                    return

        except Exception, e:
            if args.debug:
                traceback.print_exc()
                sys.exit(1)
            logger.log("INFO",
                "Process %s does not exist anymore or cannot be accessed" % str(pid))

    def check_rootkit(self):

        logger.log("INFO", "Checking for Backdoors ...")

        dp = DoublePulsar(ip="127.0.0.1", timeout=None, verbose=args.debug)

        logger.log("INFO", "Checking for Double Pulsar RDP Backdoor")
        try:
            dp_rdp_result, message = dp.check_ip_rdp()
            if dp_rdp_result:
                logger.log("ALERT", message)
            else:
                logger.log("INFO", "Double Pulsar RDP check RESULT: %s" % message)
        except Exception, e:
            logger.log("INFO", "Double Pulsar RDP check failed RESULT: Connection failure")
            if args.debug:
                traceback.print_exc()

        logger.log("INFO", "Checking for Double Pulsar SMB Backdoor")
        try:
            dp_smb_result, message = dp.check_ip_smb()
            if dp_smb_result:
                logger.log("ALERT", message)
            else:
                logger.log("INFO", "Double Pulsar SMB check RESULT: %s" % message)
        except Exception, e:
            logger.log("INFO", "Double Pulsar SMB check failed RESULT: Connection failure")
            if args.debug:
                traceback.print_exc()


    def check_c2(self, remote_system):
        # IP - exact match
        if is_ip(remote_system):
            for c2 in self.c2_server:
                # if C2 definition is CIDR network
                if is_cidr(c2):
                    if ip_in_net(remote_system, c2):
                        return True, self.c2_server[c2]
                # if C2 is ip or else
                if c2 == remote_system:
                    return True, self.c2_server[c2]
        # Domain - remote system contains c2
        # e.g. evildomain.com and dga1.evildomain.com
        else:
            for c2 in self.c2_server:
                if c2 in remote_system:
                    return True, self.c2_server[c2]

        return False,""

    def initialize_c2_iocs(self, ioc_directory):
        try:
            for ioc_filename in os.listdir(ioc_directory):
                try:
                    if 'c2' in ioc_filename:
                        with codecs.open(os.path.join(ioc_directory, ioc_filename), 'r', encoding='utf-8') as file:
                            lines = file.readlines()

                            for line in lines:
                                try:
                                    # Comments and empty lines
                                    if re.search(r'^#', line) or re.search(r'^[\s]*$', line):
                                        continue

                                    # Split the IOC line
                                    row = line.split(';')
                                    c2 = row[0]
                                    comment = row[1].rstrip(" ").rstrip("\n")

                                    # Check length
                                    if len(c2) < 4:
                                        logger.log("NOTICE","C2 server definition is suspiciously short - will not add %s" %c2)
                                        continue

                                    # Add to the LOKI iocs
                                    self.c2_server[c2.lower()] = comment

                                except Exception,e:
                                    logger.log("ERROR", "Cannot read line: %s" % line)
                                    if logger.debug:
                                        sys.exit(1)
                except OSError, e:
                    logger.log("ERROR", "No such file or directory")
        except Exception, e:
            traceback.print_exc()
            logger.log("ERROR", "Error reading Hash file: %s" % ioc_filename)

    def initialize_filename_iocs(self, ioc_directory):

        try:
            for ioc_filename in os.listdir(ioc_directory):
                if 'filename' in ioc_filename:
                    with codecs.open(os.path.join(ioc_directory, ioc_filename), 'r', encoding='utf-8') as file:
                        lines = file.readlines()

                        # Last Comment Line
                        last_comment = ""

                        for line in lines:
                            try:
                                # Empty
                                if re.search(r'^[\s]*$', line):
                                    continue

                                # Comments
                                if re.search(r'^#', line):
                                    last_comment = line.lstrip("#").lstrip(" ").rstrip("\n")
                                    continue

                                # Elements with description
                                if ";" in line:
                                    line = line.rstrip(" ").rstrip("\n\r")
                                    row = line.split(';')
                                    regex = row[0]
                                    score = row[1]
                                    if len(row) > 2:
                                        regex_fp = row[2]
                                    desc = last_comment

                                    # Catch legacy lines
                                    if not score.isdigit():
                                        desc = score        # score is description (old format)
                                        score = 60          # default value

                                # Elements without description
                                else:
                                    regex = line

                                # Replace environment variables
                                regex = replaceEnvVars(regex)
                                # OS specific transforms
                                regex = transformOS(regex, platform)

                                # If false positive definition exists
                                regex_fp_comp = None
                                if 'regex_fp' in locals():
                                    # Replacements
                                    regex_fp = replaceEnvVars(regex_fp)
                                    regex_fp = transformOS(regex_fp, platform)
                                    # String regex as key - value is compiled regex of false positive values
                                    regex_fp_comp = re.compile(regex_fp)

                                # Create dictionary with IOC data
                                fioc = {'regex': re.compile(regex), 'score': score, 'description': desc, 'regex_fp': regex_fp_comp}
                                self.filename_iocs.append(fioc)

                            except Exception, e:
                                if logger.debug:
                                    traceback.print_exc()
                                    sys.exit(1)
                                logger.log("ERROR", "Error reading line: %s" % line)

        except Exception, e:
            traceback.print_exc()
            logger.log("ERROR", "Error reading File IOC file: %s" % ioc_filename)
            logger.log("ERROR", "Please make sure that you cloned the repo or downloaded the sub repository: See "
                                "https://github.com/Neo23x0/Loki/issues/51")
            sys.exit(1)

    def initialize_yara_rules(self):

        yaraRules = ""
        dummy = ""

        try:
            for yara_rule_directory in self.yara_rule_directories:
                if not os.path.exists(yara_rule_directory):
                    continue
                logger.log("INFO", "Processing YARA rules folder {0}".format(yara_rule_directory))
                for root, directories, files in os.walk(yara_rule_directory, onerror=walk_error, followlinks=False):
                    for file in files:
                        try:

                            # Full Path
                            yaraRuleFile = os.path.join(root, file)

                            # Skip hidden, backup or system related files
                            if file.startswith(".") or file.startswith("~") or file.startswith("_"):
                                continue

                            # Extension
                            extension = os.path.splitext(file)[1].lower()

                            # Test Compile
                            try:
                                compiledRules = yara.compile(yaraRuleFile, externals={
                                    'filename': dummy,
                                    'filepath': dummy,
                                    'extension': dummy,
                                    'filetype': dummy,
                                    'md5': dummy
                                })
                                logger.log("INFO", "Initializing Yara rule %s" % file)
                            except Exception, e:
                                traceback.print_exc()
                                continue

                            # Encrypted
                            if extension == ".yar":
                                with open(yaraRuleFile, 'r') as rulefile:
                                    data = rulefile.read()
                                    yaraRules += data

                        except Exception, e:
                            logger.log("ERROR", "Error reading signature file %s ERROR: %s" % yaraRuleFile)
                            if logger.debug:
                                traceback.print_exc()
                                sys.exit(1)

            # Compile
            try:
                logger.log("INFO", "Initializing all YARA rules at once (composed string of all rule files)")
                compiledRules = yara.compile(source=yaraRules, externals={
                    'filename': dummy,
                    'filepath': dummy,
                    'extension': dummy,
                    'filetype': dummy,
                    'md5': dummy
                })
                logger.log("INFO", "Initialized all Yara rules at once")
            except Exception, e:
                traceback.print_exc()
                logger.log("ERROR", "Error during YARA rule compilation - please fix the issue in the rule set")
                sys.exit(1)

            # Add as Lokis YARA rules
            self.yara_rules.append(compiledRules)

        except Exception, e:
            logger.log("ERROR", "Error reading signature folder /signatures/")
            if logger.debug:
                traceback.print_exc()
                sys.exit(1)

    def initialize_hash_iocs(self, ioc_directory, false_positive=False):
        try:
            for ioc_filename in os.listdir(ioc_directory):
                if 'hash' in ioc_filename:
                    if false_positive and 'falsepositive' not in ioc_filename:
                        continue
                    with codecs.open(os.path.join(ioc_directory, ioc_filename), 'r', encoding='utf-8') as file:
                        lines = file.readlines()

                        for line in lines:
                            try:
                                if re.search(r'^#', line) or re.search(r'^[\s]*$', line):
                                    continue
                                row = line.split(';')
                                hash = row[0]
                                comment = row[1].rstrip(" ").rstrip("\n")
                                # Empty File Hash
                                if hash == "d41d8cd98f00b204e9800998ecf8427e" or \
                                   hash == "da39a3ee5e6b4b0d3255bfef95601890afd80709" or \
                                   hash == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855":
                                    continue
                                # Else - check which type it is
                                if len(hash) == 32:
                                    self.hashes_md5[hash.lower()] = comment
                                if len(hash) == 40:
                                    self.hashes_sha1[hash.lower()] = comment
                                if len(hash) == 64:
                                    self.hashes_sha256[hash.lower()] = comment
                                if false_positive:
                                    self.false_hashes[hash.lower()] = comment
                            except Exception,e:
                                logger.log("ERROR", "Cannot read line: %s" % line)

                    # Debug
                    if logger.debug:
                        logger.log("DEBUG", "Initialized %s hash IOCs from file %s"
                                   % (str(len(self.hashes_md5)+len(self.hashes_sha1)+len(self.hashes_sha256)), ioc_filename))

        except Exception, e:
            if logger.debug:
                traceback.print_exc()
                sys.exit(1)
            logger.log("ERROR", "Error reading Hash file: %s" % ioc_filename)

    def initialize_filetype_magics(self, filetype_magics_file):
        try:

            with open(filetype_magics_file, 'r') as config:
                lines = config.readlines()

            for line in lines:
                try:
                    if re.search(r'^#', line) or re.search(r'^[\s]*$', line) or ";" not in line:
                        continue

                    ( sig_raw, description ) = line.rstrip("\n").split(";")
                    sig = re.sub(r' ', '', sig_raw)

                    if len(sig) > self.max_filetype_magics:
                        self.max_filetype_magics = len(sig)

                    # print "%s - %s" % ( sig, description )
                    self.filetype_magics[sig] = description

                except Exception,e:
                    logger.log("ERROR", "Cannot read line: %s" % line)

        except Exception, e:
            if logger.debug:
                traceback.print_exc()
                sys.exit(1)
            logger.log("ERROR", "Error reading Hash file: %s" % filetype_magics_file)

    def initialize_excludes(self, excludes_file):
        try:
            excludes = []
            with open(excludes_file, 'r') as config:
                lines = config.read().splitlines()

            for line in lines:
                if re.search(r'^[\s]*#', line):
                    continue
                try:
                    # If the line contains something
                    if re.search(r'\w', line):
                        regex = re.compile(line, re.IGNORECASE)
                        excludes.append(regex)
                except Exception, e:
                    logger.log("ERROR", "Cannot compile regex: %s" % line)

            self.fullExcludes = excludes

        except Exception, e:
            if logger.debug:
                traceback.print_exc()
                sys.exit(1)
            logger.log("ERROR", "Error reading excludes file: %s" % excludes_file)

    def scan_regin_fs(self, fileData, filePath):

        # Code section by Paul Rascagneres, G DATA Software
        # Adapted to work with the fileData already read to avoid
        # further disk I/O

        fp = StringIO(fileData)
        SectorSize=fp.read(2)[::-1]
        MaxSectorCount=fp.read(2)[::-1]
        MaxFileCount=fp.read(2)[::-1]
        FileTagLength=fp.read(1)[::-1]
        CRC32custom=fp.read(4)[::-1]

        # original code:
        # fp.close()
        # fp = open(filePath, 'r')

        # replaced with the following:
        fp.seek(0)

        data=fp.read(0x7)
        crc = binascii.crc32(data, 0x45)
        crc2 = '%08x' % (crc & 0xffffffff)

        logger.log("DEBUG", "Regin FS Check CRC2: %s" % crc2.encode('hex'))

        if CRC32custom.encode('hex') == crc2:
            logger.log("ALERT", "Regin Virtual Filesystem MATCH: %s" % filePath)

    def get_file_data(self, filePath):
        fileData = ""
        try:
            # Read file complete
            with open(filePath, 'rb') as f:
                fileData = f.read()
        except Exception, e:
            if logger.debug:
                traceback.print_exc()
            logger.log("DEBUG", "Cannot open file %s (access denied)" % filePath)
        finally:
            return fileData

    def script_stats_analysis(self, data):
        """
        Doing a statistical analysis for scripts like PHP, JavaScript or PowerShell to
        detect obfuscated code
        :param data:
        :return: message, score
        """
        anomal_chars = [r'^', r'{', r'}', r'"', r',', r'<', r'>', ';']
        anomal_char_stats = {}
        char_stats = {"upper": 0, "lower": 0, "numbers": 0, "symbols": 0, "spaces": 0}
        anomalies = []
        c = Counter(data)
        anomaly_score = 0

        # Check the characters
        for char in c.most_common():
            if char[0] in anomal_chars:
                anomal_char_stats[char[0]] = char[1]
            if char[0].isupper():
                char_stats["upper"] += char[1]
            elif char[0].islower():
                char_stats["lower"] += char[1]
            elif char[0].isdigit():
                char_stats["numbers"] += char[1]
            elif char[0].isspace():
                char_stats["spaces"] += char[1]
            else:
                char_stats["symbols"] += char[1]
        # Totals
        char_stats["total"] = len(data)
        char_stats["alpha"] = char_stats["upper"] + char_stats["lower"]

        # Detect Anomalies
        if char_stats["alpha"] > 40 and char_stats["upper"] > (char_stats["lower"] * 0.9):
            anomalies.append("upper to lower ratio")
            anomaly_score += 20
        if char_stats["symbols"] > char_stats["alpha"]:
            anomalies.append("more symbols than alphanum chars")
            anomaly_score += 40
        for ac, count in anomal_char_stats.iteritems():
            if (count/char_stats["alpha"]) > 0.05:
                anomalies.append("symbol count of '%s' very high" % ac)
                anomaly_score += 40

        # Generate message
        message = "Anomaly detected ANOMALIES: '{0}'".format("', '".join(anomalies))
        if anomaly_score > 40:
            return message, anomaly_score

        return "", 0


def get_application_path():
    try:
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(os.path.realpath(sys.executable))
        else:
            application_path = os.path.dirname(os.path.realpath(__file__))
        if "~" in application_path and platform == "windows":
            # print "Trying to translate"
            # print application_path
            application_path = win32api.GetLongPathName(application_path)
        #if args.debug:
        #    logger.log("DEBUG", "Application Path: %s" % application_path)
        return application_path
    except Exception, e:
        print "Error while evaluation of application path"
        traceback.print_exc()
        if args.debug:
            sys.exit(1)


def updateLoki(sigsOnly):
    logger.log("INFO", "Starting separate updater process ...")
    pArgs = []

    # Updater
    if os.path.exists(os.path.join(get_application_path(), 'loki-upgrader.exe')) and platform == "windows":
        pArgs.append('loki-upgrader.exe')
    elif os.path.exists(os.path.join(get_application_path(), 'loki-upgrader.py')):
        pArgs.append('python')
        pArgs.append('loki-upgrader.py')
    else:
        logger.log("ERROR", "Cannot find neither thor-upgrader.exe nor thor-upgrader.py in the current workign directory.")

    if sigsOnly:
        pArgs.append('--sigsonly')
        p = Popen(pArgs, shell=False)
        p.communicate()
    else:
        pArgs.append('--detached')
        Popen(pArgs, shell=False)


def walk_error(err):
    try:
        if "Error 3" in str(err):
            logger.log('ERROR', removeNonAsciiDrop(str(err)))
        elif args.debug:
            print "Directory walk error"
            sys.exit(1)
    except UnicodeError, e:
        print "Unicode decode error in walk error message"


# CTRL+C Handler --------------------------------------------------------------
def signal_handler(signal_name, frame):
    try:
        print "------------------------------------------------------------------------------\n"
        logger.log('INFO', 'LOKI\'s work has been interrupted by a human. Returning to Asgard.')
    except Exception, e:
        print 'LOKI\'s work has been interrupted by a human. Returning to Asgard.'
    sys.exit(0)


# MAIN ################################################################
if __name__ == '__main__':

    # Signal handler for CTRL+C
    signal_module.signal(signal_module.SIGINT, signal_handler)

    # Computername
    if platform == "linux" or platform == "osx":
        t_hostname = os.uname()[1]
    else:
        t_hostname = os.environ['COMPUTERNAME']

    # Parse Arguments
    parser = argparse.ArgumentParser(description='Loki - Simple IOC Scanner')
    parser.add_argument('-p', help='Path to scan', metavar='path', default='C:\\')
    parser.add_argument('-s', help='Maximum file size to check in KB (default 5000 KB)', metavar='kilobyte', default=5000)
    parser.add_argument('-l', help='Log file', metavar='log-file', default='loki-%s.log' % t_hostname)
    parser.add_argument('-r', help='Remote syslog system', metavar='remote-loghost', default='')
    parser.add_argument('-a', help='Alert score', metavar='alert-level', default=100)
    parser.add_argument('-w', help='Warning score', metavar='warning-level', default=60)
    parser.add_argument('-n', help='Notice score', metavar='notice-level', default=40)
    parser.add_argument('--printAll', action='store_true', help='Print all files that are scanned', default=False)
    parser.add_argument('--allreasons', action='store_true', help='Print all reasons that caused the score', default=False)
    parser.add_argument('--noprocscan', action='store_true', help='Skip the process scan', default=False)
    parser.add_argument('--nofilescan', action='store_true', help='Skip the file scan', default=False)
    parser.add_argument('--scriptanalysis', action='store_true', help='Activate script analysis (beta)', default=False)
    parser.add_argument('--rootkit', action='store_true', help='Skip the rootkit check', default=False)
    parser.add_argument('--noindicator', action='store_true', help='Do not show a progress indicator', default=False)
    parser.add_argument('--reginfs', action='store_true', help='Do check for Regin virtual file system', default=False)
    parser.add_argument('--dontwait', action='store_true', help='Do not wait on exit', default=False)
    parser.add_argument('--intense', action='store_true', help='Intense scan mode (also scan unknown file types and all extensions)', default=False)
    parser.add_argument('--csv', action='store_true', help='Write CSV log format to STDOUT (machine prcoessing)', default=False)
    parser.add_argument('--onlyrelevant', action='store_true', help='Only print warnings or alerts', default=False)
    parser.add_argument('--nolog', action='store_true', help='Don\'t write a local log file', default=False)
    parser.add_argument('--update', action='store_true', default=False, help='Update the signatures from the "signature-base" sub repository')
    parser.add_argument('--debug', action='store_true', default=False, help='Debug output')

    args = parser.parse_args()

    # Remove old log file
    if os.path.exists(args.l):
        os.remove(args.l)

    # Logger
    logger = LokiLogger(args.nolog, args.l, t_hostname, args.r, args.csv, args.onlyrelevant, args.debug,
                        platform=platform, caller='main')

    # Update
    if args.update:
        updateLoki(sigsOnly=False)
        sys.exit(0)

    logger.log("NOTICE", "Starting Loki Scan SYSTEM: {0} TIME: {1} PLATFORM: {2}".format(
        t_hostname, getSyslogTimestamp(), platform))

    # Loki
    loki = Loki(args.intense)

    # Check if admin
    isAdmin = False
    if platform == "windows":
        if shell.IsUserAnAdmin():
            isAdmin = True
            logger.log("INFO", "Current user has admin rights - very good")
        else:
            logger.log("NOTICE", "Program should be run 'as Administrator' to ensure all access rights to process memory and file objects.")
    else:
        if os.geteuid() == 0:
            isAdmin = True
            logger.log("INFO", "Current user is root - very good")
        else:
            logger.log("NOTICE", "Program should be run as 'root' to ensure all access rights to process memory and file objects.")

    # Set process to nice priority ------------------------------------
    if platform == "windows":
        setNice(logger)

    # Scan Processes --------------------------------------------------
    resultProc = False
    if not args.noprocscan and platform == "windows":
        if isAdmin:
            loki.scan_processes()
        else:
            logger.log("NOTICE", "Skipping process memory check. User has no admin rights.")

    # Scan for Rootkits -----------------------------------------------
    if args.rootkit and platform == "windows":
        loki.check_rootkit()

    # Scan Path -------------------------------------------------------
    # Set default
    defaultPath = args.p
    if ( platform == "linux" or platform == "osx" ) and defaultPath == "C:\\":
        defaultPath = "/"

    resultFS = False
    if not args.nofilescan:
        loki.scan_path(defaultPath)

    # Result ----------------------------------------------------------
    logger.log("NOTICE", "Results: {0} alerts, {1} warnings, {2} notices".format(logger.alerts, logger.warnings, logger.notices))
    if logger.alerts:
        logger.log("RESULT", "Indicators detected!")
        logger.log("RESULT", "Loki recommends checking the elements on Virustotal.com or Google and triage with a "
                             "professional triage tool like THOR APT Scanner in corporate networks.")
    elif logger.warnings:
        logger.log("RESULT", "Suspicious objects detected!")
        logger.log("RESULT", "Loki recommends a deeper analysis of the suspicious objects.")
    else:
        logger.log("RESULT", "SYSTEM SEEMS TO BE CLEAN.")

    logger.log("NOTICE", "Finished LOKI Scan SYSTEM: %s TIME: %s" % (t_hostname, getSyslogTimestamp()))

    if not args.dontwait:
        print " "
        raw_input("Press Enter to exit ...")
