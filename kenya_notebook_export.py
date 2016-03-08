"""Export notebooks for Kenya."""
from app.shared.models import Notebook

kenya_notebooks = {
    '5677eeb9394eb30541b77684': 'Huku_1.xls',
    '565d69924853f104e516f7ef': 'Huku_2.xls',
    '55e85cd37b1e070003a7bedd': 'Huku_3.xls',
    '55ddaf4c7b0ff00018b6dc24': 'Huku_4.xls',
    '56b47829d4dabb03899bdd5e': 'Kaga_1.xls',
    '5677f8097031fb056766dfe6': 'Kaga_2.xls',
    '55ddcdb6a44d92002906af05': 'Kaga_3.xls',
    '56936b6d1d456f003dae001c': 'Ruai_1.xls',
    '55eed2c3392e0901e115fc84': 'Ruai_2.xls',
    '55e99ec84d77d70175bc1c03': 'Ruai_3.xls',
    '563868785151ae0188b06327': 'Mwea_B_1.xls',
    '55ddbe1b7b0ff00025b6dc24': 'Mwea_B_2.xls',
    '55ed51d801dfa1012e1e06b0': 'Maka_1.xls',
    '55e99ebe4d77d7016ebc1c03': 'Maka_2.xls',
    '55eed2d0392e0901eb15fc84': 'Nkando_1.xls',
    '55e9a7415ef13b01d5e8f528': 'Nkando_2.xls',
    '55e9ac325ef13b01dae8f528': 'Jikaze_1.xls',
    '56d957bb0c7353087f5956fb': 'Tumaini_1.xls',
    '55eedfd3392e0901f015fc84': 'Tumaini_2.xls',
    '55e9a12e4d77d7017cbc1c03': 'Tumaini_3.xls',
    '55f29dd3a397e8018e4c2656': 'Miarage_B_1.xls',
    '55e9ac355ef13b01dfe8f528': 'Miarage_B_2.xls',
    '56d96be878633505189dce31': 'Batian_1.xls',
    '56ced612d578d6448e1677b4': 'Batian_2.xls',
    '56ab27360dbc6a02c589e800': 'Batian_3.xls',
    '563890f97b2444030f64a5bc': 'Batian_4.xls',
    '55fbf4f0a67e5301793b0808': 'Batian_5.xls',
    '55edac1c9b0260016e588af0': 'Batian_6.xls',
    '56c318722d6bc8001680523f': 'Gitarga_1.xls',
    '563883037b244402a164a5bc': 'Gitarga_2.xls',
    '55fbe450a67e53016e3b0808': 'Gitarga_3.xls',
    '55f7af6f566626015696dfdb': 'Gitarga_4.xls',
    '56b461da65744d0b873aa9ed': 'Chumvi_1.xls',
    '5639f58bcca58b014d9ab6bf': 'Chumvi_2.xls',
    '5603c2b380415902753fc050': 'Chumvi_3.xls',
    '55f66354f102ab0139de8d0a': 'Chumvi_4.xls',
    '55fbcd15408a21019f5530bf': 'Chumvi_5.xls',
    '5677c51c394eb304f1b77684': 'Wiumiririe_1.xls',
    '55fbb98aa67e5300f53b0808': 'Wiumiririe_2.xls',
    '552e60b1f14c10005b4d6085': 'Wiumiririe_3.xls'
}


def export_notebooks(notebook_dict=None):
    """Export the notebooks."""
    path = "/Users/kellycaylor/Dropbox (PE)/files_for_drew/"
    for notebook_id in notebook_dict.keys():
        notebook = Notebook.objects(id=notebook_id).first()
        filename = "{path}{file}".format(
            path=path,
            file=notebook_dict[notebook_id]
        )
        notebook.xls(filename=filename)
