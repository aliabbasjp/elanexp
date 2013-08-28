#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      ALI
#
# Created:     22/08/2013
# Copyright:   (c) ALI 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import collections

class NestedDict(collections.OrderedDict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


##def merge(a, b, path=None):
##    "merges b into a"
##    if path is None: path = []
##    for key in b:
##        if key in a:
##            if isinstance(a[key], dict) and isinstance(b[key], dict):
##                merge(a[key], b[key], path + [str(key)])
##            elif a[key] == b[key]:
##                pass # same leaf value
##            else:
##                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
##        else:
##            a[key] = b[key]
##    return a

##try:
##    from collections import Mapping
##except ImportError:
##    Mapping = dict
##
##def merge(*dicts):
##    """
##    Return a new dictionary that is the result of merging the arguments together.
##    In case of conflicts, later arguments take precedence over earlier arguments.
##    """
##    updated = {}
##    # grab all keys
##    keys = set()
##    for d in dicts:
##        keys = keys.union(set(d))
##
##    for key in keys:
##        values = [d[key] for d in dicts if key in d]
##        # which ones are mapping types? (aka dict)
##        maps = [value for value in values if isinstance(value, Mapping)]
##        if maps:
##            # if we have any mapping types, call recursively to merge them
##            updated[key] = merge(*maps)
##        else:
##            # otherwise, just grab the last value we have, since later arguments
##            # take precedence over earlier arguments
##            updated[key] = values[-1]
##    return updated


class YamlReaderError(Exception):
    pass

def merge(a, b):
    """merges b into a and return merged result

    NOTE: tuples and arbitrary objects are not handled as it is totally ambiguous what should happen"""
    key = None
    # ## debug output
    # sys.stderr.write("DEBUG: %s to %s\n" %(b,a))
    try:
        if a is None or isinstance(a, str) or isinstance(a, unicode) or isinstance(a, int) or isinstance(a, long) or isinstance(a, float):
            # border case for first run or if a is a primitive
            a = b
        elif isinstance(a, list):
            # lists can be only appended
            if isinstance(b, list):
                # merge lists
                a.extend(b)
            else:
                # append to list
                a.append(b)
        elif isinstance(a, dict):
            # dicts must be merged
            if isinstance(b, dict):
                for key in b:
                    if key in a:
                        a[key] = merge(a[key], b[key])
                    else:
                        a[key] = b[key]
            else:
                raise YamlReaderError('Cannot merge non-dict "%s" into dict "%s"' % (b, a))
        elif isinstance(a,tuple):
            # tuples as keys must be merged
            if isinstance(b, tuple):
                raise YamlReaderError('NOT IMPLEMENTED "%s" into "%s"' % (b, a))
        else:
            raise YamlReaderError('NOT IMPLEMENTED "%s" into "%s"' % (b, a))
    except TypeError, e:
        raise YamlReaderError('TypeError "%s" in key "%s" when merging "%s" into "%s"' % (e, key, b, a))
    return a