rule disco_squirell : trojan
{
    meta:
        description = "Example for DiscoSquirell malware"
        threat_level = "APT"
        in_the_wild = true

    strings:
        $pdb_path = "C:\\Users\\John\\documents\\visual studio 2017\\Projects\\DiscoSquirrel\\DiscoSquirrel\\obj\\Release\\DiscoSquirrel.pdb"
        $original_file_name = "DiscoSquirrel.exe" wide
        $dropped_file_path = "\\Microsoft\\Windows\\Explorer\\ExplorerDebugLog.etl" wide
        $http_request_post = "POST" wide
        $stolen_file_extension_docx = ".docx" wide
        $stolen_file_extension_pdf = ".pdf" wide
        $persistence_function_name = "MakePersistent"
        $fake_windows_executable = "\\Microsoft\\Windows\\smss.exe" wide
    
    condition:
        all of them
}