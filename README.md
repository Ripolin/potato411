#potato411

T411 torrent provider implementation for CouchPotato. It uses the official [T411's API] (https://api.t411.ch) without parsing any HTML files.

##How to install

Once checkout, copy the `t411` directory directly under the `CP_CONFIG_DIR/data/customs_plugin` directory of your CouchPotato server. When it's done, restart it. You'll see a new entry T411 on the Settings>Searcher location.

##Development

Be sure you're running the latest version of [Python 2.7] (http://python.org/).

### Tests

More informations in the [test directory] (test).

##Issues

Use issue tracker.

##Additional informations

It's not the purpose of this plugin to manage additional languages for searching torrents. As lucky we are, CouchPotato does this job. Just verify in your `config.ini` file in your `CP_CONFIG_DIR` directory that you have the property `languages` correctly filled in the `core` section.

Example :

```ini
[core]
...
languages = fr
```

Now CouchPotato will retrieve any french titles of searching movies. Just select it and the plugin does the rest.
