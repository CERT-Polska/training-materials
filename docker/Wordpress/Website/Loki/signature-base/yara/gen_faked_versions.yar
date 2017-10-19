rule Fake_AdobeReader_EXE
    {
    meta:
        description = "Detects an fake AdobeReader executable based on filesize OR missing strings in file"
        date = "2014-09-11"
        author = "Florian Roth"
        score = 50
    strings:
        $s1 = "Adobe Systems" ascii
        $s2 = "Adobe Reader" ascii wide
    condition:
        uint16(0) == 0x5a4d and
        filename matches /AcroRd32.exe/i and
        not $s1 in (filesize-2500..filesize)
        and not $s2
}

rule Fake_FlashPlayerUpdaterService_EXE
    {
    meta:
        description = "Detects an fake AdobeReader executable based on filesize OR missing strings in file"
        date = "2014-09-11"
        author = "Florian Roth"
        score = 50
    strings:
        $s1 = "Adobe Systems Incorporated" ascii wide
    condition:
        uint16(0) == 0x5a4d and
        filename matches /FlashPlayerUpdateService.exe/i and
        not $s1
}
