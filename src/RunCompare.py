__author__ = 'nico'
import logging

import CustomUtils as CustomUtils
import src.screenshots.comparison.Comparator
from src.database.Screenshots_DB import Screenshots_DB
from src.database.Pdiffs_DB import Pdiffs_DB

logger = logging.getLogger('obs.Compare')


def run(testparams, config):
    expected_keys = ["comparisons"]
    testdata = CustomUtils.json_parse(testparams, expected_keys)
    cfgdata = CustomUtils.json_parse(config)

    results = _main(testdata, cfgdata)

    print(results)
    CustomUtils.save_dict_to_json(results, testdata.get("results"))


def _main(testdata, cfgdata):
    # Initialize databases (models; no connection is made yet)
    dbcheck = True if cfgdata.get("check_database_schema") else False
    sshots_db = Screenshots_DB(cfgdata.get("database_path"))
    pdiffs_db = Pdiffs_DB(cfgdata.get("database_path"), safe=dbcheck)  # TODO: Save diffs in DB

    # Determine which comparison method will be used
    img_pairs = testdata.get("comparisons")
    actions  = testdata.get("actions")

    final_results = {"actions": []}
    for action in actions:
        try:
            action_name = action.get("name")
            action_parameters = action.get("parameters")
            # Get specified function through reflection
            function = getattr(src.screenshots.comparison.Comparator, action_name)
        except AttributeError:
            logger.critical(
                'The action requested is not found in Comparator.py! You can implement new comparison actions in there.')
            final_results["status"] = {"name":"warning",
                                       "reason": "action requested not recognized",
                                       "data": "requested: %s" % action.get("name")
            }
            continue
        for img_pair in img_pairs:
            # Replace DB IDs for filenames if necessary
            img_pair = [sshots_db.get_by_id(c) if isinstance(c, int) else c for c in img_pair]
            logger.info("Comparing: %s and %s using %s" % (img_pair[0], img_pair[1], action_name))
            partial = {"sources": img_pair}

            # Call specified comparison method with kwargs if they were provided
            try:
                compare_result = function(img_pair[0], img_pair[1], **action_parameters) if action_parameters is not None else function(img_pair[0], img_pair[1])
            except TypeError, e:
                if "got an unexpected keyword argument" in e.message:
                    #func_name = comparison_method.get("name")

                    func_args = ", ".join(function.func_code.co_varnames[2:function.func_code.co_argcount])
                    if func_args != "":
                        err = "Tried to run '%s' with the wrong parameters. It requires: %s" % (action_name, func_args)
                    else:
                        err = "Tried to run '%s' with parameters. It requires none." % action_name
                    logger.error(err)
                    final_results["status"] = {"name": "warning", "reason": err}
                    continue
            partial.update(compare_result)

            if "reason" in compare_result.keys():
                final_results["status"] = {"name": "warning"}

            final_results["actions"].append(partial)

    if "status" not in final_results.keys():
        final_results["status"] = {"name": "success"}
    return final_results
