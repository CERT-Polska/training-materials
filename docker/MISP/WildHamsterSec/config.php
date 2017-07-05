<?php
$config = array(
	'debug'            => 0,
	'Security'         =>
		array(
			'level'      => 'medium',
			'salt' => 'YbEOE+jHcO4kWhnJn49HdDb4XEHDod5mIG1+vseXQas=',
			'cipherSeed' => '',
			//'auth'=>array('CertAuth.Certificate'), // additional authentication methods
			//'auth'=>array('ShibbAuth.ApacheShibb'),
		),
	'MISP'             =>
		array(
			'baseurl' => 'https://172.17.0.1:20443',
			'footermidleft'                  => '',
			'footermidright'                 => '',
			'org'                            => 'WILDHAMSTERSEC',
			'showorg'                        => true,
			'threatlevel_in_email_subject'   => true,
			'email_subject_TLP_string'       => 'TLP Amber',
			'email_subject_tag'              => 'tlp',
			'email_subject_include_tag_name' => true,
			'background_jobs'                => true,
			'cached_attachments'             => true,
			'email'                          => 'admin@localhost',
			'contact'                        => 'admin@localhost',
			'cveurl'                         => 'http://cve.circl.lu/cve/',
			'disablerestalert'               => false,
			'default_event_distribution'     => '1',
			'default_attribute_distribution' => 'event',
			'tagging'                        => true,
			'full_tags_on_event_index'       => true,
			'attribute_tagging'              => true,
			'full_tags_on_attribute_index'   => true,
			'footer_logo'                    => '',
			'take_ownership_xml_import'      => false,
			'unpublishedprivate'             => false,
			'disable_emailing'               => false,
			'live'			         => true,
			'host_org_id'		         => 1,
			'proposals_block_attributes'	 => true,
		),
	'GnuPG'            =>
		array(
			'onlyencrypted'     => false,
			'email'             => '',
			'homedir'           => '/usr/bin/gpg',
			'password'          => '',
			'bodyonlyencrypted' => false,
		),
	'SMIME'            =>
		array(
			'enabled'          => false,
			'email'            => '',
			'cert_public_sign' => '',
			'key_sign'         => '',
			'password'         => '',
		),
	'Proxy'            =>
		array(
			'host'     => '',
			'port'     => '',
			'method'   => '',
			'user'     => '',
			'password' => '',
		),
	'SecureAuth'       =>
		array(
			'amount' => 5,
			'expire' => 300,
		),
	// Uncomment the following to enable client SSL certificate authentication
	/*
	'CertAuth'         =>
		array(
			'ca'           => array('FIRST.Org'), // allowed CAs
			'caId'         => 'O',          // which attribute will be used to verify the CA
			'userModel'    => 'User',       // name of the User class to check if user exists
			'userModelKey' => 'nids_sid',   // User field that will be used for querying
			'map'          => array(        // maps client certificate attributes to User properties
				'O'            => 'org',
				'emailAddress' => 'email',
			),
			'syncUser'     => true,         // should the User be synchronized with an external REST API
			'userDefaults' => array(          // default user attributes, only used when creating new users
				'role_id' => 4,
			),
			'restApi'      => array(        // API parameters
				'url'     => 'https://example.com/data/users',  // URL to query
				'headers' => array(),                           // additional headers, used for authentication
				'param'   => array('email' => 'email'),       // query parameters to add to the URL, mapped to User properties
				'map'     => array(                            // maps REST result to the User properties
					'uid'        => 'nids_sid',
					'team'       => 'org',
					'email'      => 'email',
					'pgp_public' => 'gpgkey',
				),
			),
			'userDefaults' => array('role_id' => 3),          // default attributes for new users
		),
	*/
	/*
	'ApacheShibbAuth'  =>                      // Configuration for shibboleth authentication
		array(
			'apacheEnv'         => 'REMOTE_USER',        // If proxy variable = HTTP_REMOTE_USER
			'ssoAuth'           => 'AUTH_TYPE',
			'MailTag'           => 'EMAIL_TAG',
			'OrgTag'            => 'FEDERATION_TAG',
			'GroupTag'          => 'GROUP_TAG',
			'GroupSeparator'    => ';',
			'GroupRoleMatching' => array(                // 3:User, 1:admin. May be good to set "1" for the first user
				'group_three' => 3,
				'group_two'   => 2,
				'group_one'   => 1,
			),
			'DefaultRoleId'     => 3,
			'DefaultOrg'        => 'DEFAULT_ORG',
		),
	*/
	// Warning: The following is a 3rd party contribution and still untested (including security) by the MISP-project team.
	// Feel free to enable it and report back to us if you run into any issues.
	//
	// Uncomment the following to enable Kerberos authentication
	// needs PHP LDAP support enabled (e.g. compile flag --with-ldap or Debian package php5-ldap)
	/*
	'ApacheSecureAuth' => // Configuration for kerberos authentication
		array(
			'apacheEnv'          => 'REMOTE_USER',           // If proxy variable = HTTP_REMOTE_USER
			'ldapServer'         => 'ldap://example.com',   // FQDN or IP
			'ldapProtocol'       => 3,
			'ldapReaderUser'     => 'cn=userWithReadAccess,ou=users,dc=example,dc=com', // DN ou RDN LDAP with reader user right
			'ldapReaderPassword' => 'UserPassword', // the LDAP reader user password
			'ldapDN'             => 'dc=example,dc=com',
            'ldapSearchFilter'   => '', // Search filter to limit results from ldapsearh fx to specfic group. FX
	 		//'ldapSearchFilter'   => '(objectclass=InetOrgPerson)(!(nsaccountlock=True))(memberOf=cn=misp,cn=groups,cn=accounts,dc=example,dc=com)',
			'ldapSearchAttribut' => 'uid',          // filter for search
			'ldapFilter'         => array(
				'mail',
            //	'memberOf', //Needed filter if roles should be added depending on group membership.
			),
			'ldapDefaultRoleId'  => 3,               // 3:User, 1:admin. May be good to set "1" for the first user
            //ldapDefaultRoleId can also be set as an array to support creating users into different group, depending on ldap membership.
			//This will only work if the ldap server supports memberOf
			//'ldapDefaultRoleId'  => array(
            //                         'misp_admin' => 1,
            //                         'misp_orgadmin' => 2,
            //                         'misp_user' => 3,
            //                         'misp_publisher' => 4,
            //                         'misp_syncuser' => 5,
            //                         'misp_readonly' => 6,
            //                         ),
			//
			'ldapDefaultOrg'     => '1',      // uses 1st local org in MISP if undefined
		),
	*/
);
