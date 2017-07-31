rule turbo_bear : trojan
{
    meta:
        description = "Example for TurboBear malware"
        threat_level = "Spam"
        in_the_wild = true

    strings:
        $original_file_name = "TurboBear.exe" wide
        $computer_info_registry_entry = "get_MachineName" wide
        $computer_info_function_name = "SendComputerInfoToC2"
        $persistence_function_name = "MakePersistent"
        $serializer_name = "JavaScriptSerializer"
    
    condition:
        4 of them
}