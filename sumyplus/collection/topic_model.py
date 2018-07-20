#
#
#
#
import os
import json
import sumyplus


def get_valid_mdocs(keyword, collection):
    """Looks at each metadata file and returns if it contains the keyword"""
    mdocs = []
    for metadoc in collection["metadocs"]:
        if keyword in set(metadoc["keywords"]):
            mdocs.append("\\".join([collection["directory"], metadoc["name"]]))
    return mdocs


def get_valid_smdocs(keyword, collection):
    """Looks at each supermetadata file and returns if it contains the keyword"""
    smdocs = []
    for supermetadoc in collection["supermetadocs"]:
        if keyword in set(supermetadoc["keywords"]):
            smdocs.append("\\".join([supermetadoc["directory"], supermetadoc["filename"]]))
    return smdocs


def collect_metafiles(keyword, smdoc):
    """Takes a starting supermetadata file and recursively collects all the lowest level metadata files that contain the keyword"""
    assert type(smdoc) is str, "Please specify a valid starting supermetadata file."
    smdocs = [smdoc]
    first_smdoc = True
    method_mdocs = []
    while smdocs:
        # Get smdoc to process
        smdoc_file = smdocs.pop()
        # print('popped_file', smdoc_file)
        with open(smdoc_file) as fobj:
            level_data = json.load(fobj)
            if first_smdoc:
                # Check to make sure keyword is even in entire collection
                keywords = set(level_data["keywords"])
                assert keyword in keywords, f"The keyword '{keyword}' is not in the collection."
                first_smdoc = False

        # Get all smdocs and mdocs at level
        method_mdocs.extend(get_valid_mdocs(keyword, level_data))
        smdocs.extend(get_valid_smdocs(keyword, level_data))

    assert not smdocs, "Something went wrong and not all smdocs were processed successfully."
    return method_mdocs


def get_mdoc_summary(mdoc, keyword, naive_threshold=0):
    with open(mdoc) as fobj:
        data = json.load(fobj)
        if naive_threshold != 0:
            limit = sorted(data["keywords"].values(), reverse=True)[naive_threshold]
            if data["keywords"][keyword] > limit:
                return data["summary"]
            else:
                return []
        else:
            return data["summary"]


def create_composite_summary(mdocs, thresh):
    composite_summary = []
    n_used = 0
    for metadoc in mdocs:
        single_summary = get_mdoc_summary(metadoc, thresh)
        if single_summary:
            composite_summary.extend(single_summary)
            n_used += 1
    return composite_summary, n_used


class Query(object):
    """"""
    def __init__(self, metadoc_path):
        self.path = metadoc_path
        assert os.path.isdir(os.path.abspath(self.path)), "The specified path is not a directory."
        #
        self.meta_head = [file for file in os.listdir(os.path.abspath(self.path)) if file.endswith("smdoc")]
        assert self.meta_head, "Super-metadata file is missing for the collection path specified."
        top_metafile = self.meta_head[0]
        self.metapath = "\\".join([os.path.abspath(self.path), top_metafile])
        #

    def query_metafiles(self, keyword):
        """"""
        mdocs = collect_metafiles(keyword, self.metapath)
        print(f"The search term '{keyword}' appeared in {len(mdocs)} documents within the collection.")
        return mdocs

    def get_composite_summary(self, keyword):
        """"""
        mdocs = self.query_metafiles(keyword)
        composite_summary, n_used = create_composite_summary(mdocs)
        print(f"The following composite summary for the keyword '{keyword}' was created from {n_used} files meeting the requirements.")
        print(f"\n{composite_summary}")
