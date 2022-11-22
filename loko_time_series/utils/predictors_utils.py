#
#
# def save_pipeline(pipeline, branch, history_limit, repo_path, dao=None):
#     path = repo_path / "predictors" / pipeline.id
#     fsvc = FileSystemVC(path, history_limit) if not dao else dao(path)
#     if branch in fsvc.branches:
#         fsvc.checkout(branch)
#     else:
#         fsvc.create_branch(branch)
#     status_list = [dict(fname=fname, content=step) for fname, step in pipeline.steps]
#     fsvc.commit(status_list, date=pipeline.date)
#     fsvc.push()
