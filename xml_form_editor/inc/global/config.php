<?php
	// todo add the display config

	define("DEBUG", false);
	define("LOG_LEVEL", "notice"); // Log level: {notice, debug, info, warn, error} // TODO Implement it

	define("CACHED", false); // todo implement it

	define("PROJECT_NAME", "Material Data Curator");

	define("TOOL_NAME", "");
	define("TOOL_TITLE", "");
	define("TOOL_VERSION", "0.4c");
	define("TOOL_RELEASE_DATE", ""); // xxx unused...

	define("_ROOT_", dirname(dirname(dirname(__FILE__)))); // todo only use the session variable
	$_SESSION['config']['_ROOT_'] = _ROOT_;

	$_SESSION['config']['_XSDFOLDER_'] = $_SESSION['config']['_ROOT_'].'/resources/files/schemas';

	//todo configuration of the pages
	//todo log configuration