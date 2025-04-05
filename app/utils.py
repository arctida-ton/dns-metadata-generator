from typing import Dict

from fastapi import HTTPException
from pytoniq_core import Cell, Address, begin_cell, StateInit

SUPPORTED_TLD = ["ton", "gram"]

ITEM_CODES = {
    "base": "b5ee9c72410216010003af000114ff00f4a413f4bcf2c80b01020162020f0202ce030c020120040b02f30c8871c02497c0f83434c0c05c6c2497c0f83e90087c007e900c7e800c5c75c87e800c7e800c1cea6d0000b4c7f4cffc0081acf8c08a3000638f440e17c20ccc4871c17cb8645c20843a282aff885b60101c20043232c15401f3c594017e808572da84b2c7f2cfc89bace51633c5c0644cb88072407ec0380a20050701f65f03323435355233c705f2e1916d70c8cb07f400c904fa40d4d420c701c0008e42fa00218e3a821005138d9170c82acf165003cf162604503373708010c8cb055007cf165005fa0215cb6a12cb1fcb3f226eb39458cf17019132e201c901fb00915be29130e2820afaf08070fb027082107b4b42e62703076d8306060054708010c8cb055007cf165005fa0215cb6a12cb1fcb3f226eb39458cf17019132e201c901fb004503f00302e082105fcc3d14ba8e8a3810394816407315db3ce03a3a2682102fcb26a2ba8e3e3035365b347082108b77173504c8cbff58cf164430128040708010c8cb055007cf165005fa0215cb6a12cb1fcb3f226eb39458cf17019132e201c901fb00e0350582104eb1f0f9bae3025f08840ff2f0080a01f65137c705f2e191fa4021f001fa40d20031fa000c820afaf080a121945315a0a1de22d70b01c300209206a19136e220c2fff2e192218e3dc8500acf16500ccf16821005138d9171245146104f50f2708010c8cb055007cf165005fa0215cb6a12cb1fcb3f226eb39458cf17019132e201c901fb0094102c395be20209007e8e3428f00148508210d53276db016d71708010c8cb055007cf165005fa0215cb6a12cb1fcb3f226eb39458cf17019132e201c901fb0093303436e25504f003007a5153c705f2e19101d3ff20d74ac20008d0d30701c000f2e19cf404300898d43040178307f417983050068307f45b30e270c8cb07f400c910355512f00300113e910c30003cb853600201200d0e00433b513434fffe900835d27080271fc07e903535350c04118411780c1c165b5b5b5b600023017232ffd40133c59633c5b33333327b55200201201011004bbc265f801282b2f82b8298064459ba37b74678b658382680a678b09e58380e8678b6583e4e840201201213000db8fcff0023031802012014150011b64a5e0042cbe0da1000c7b461843ae9240f152118001e5c08de004204cbe0da1a60e038001e5c339e8086007ae140f8001e5c33b84111c466105e033e04883dcb11fb64ddc4964ad1ba06b879240dc23572f37cc5caaab143a2fffbc4180012660f003c003060fe81edf4260f00304c1dd84e",
    # *.pseudonym.ton
    "94804456238319738655725665826558209992428117612026642684317067795890505825106": "b5ee9c72410217010003bd000114ff00f4a413f4bcf2c80b0102016202100202ce030d020120040c04b30c8871c02497c0f83434c0c05c6c2497c0f83e90087c007e900c7e800c5c75c87e800c7e800c1cea6d0000b4c7f4cffc0081acf8c08a300078c08a208417f30f452ea3a28e040e5205901cc576cf380e8e89a0840bf2c9a8aea00507080a01f65f03323435355233c705f2e1916d70c8cb07f400c904fa40d4d420c701c0008e42fa00218e3a821005138d9170c82acf165003cf162604503373708010c8cb055007cf165005fa0215cb6a12cb1fcb3f226eb39458cf17019132e201c901fb00915be29130e2820afaf08070fb027082107b4b42e62703076d8306060054708010c8cb055007cf165005fa0215cb6a12cb1fcb3f226eb39458cf17019132e201c901fb004503f003009210355f0535355b21c705f2e191708210e8a0abfe21c805fa403015cf16103441308040708010c8cb055007cf165005fa0215cb6a12cb1fcb3f226eb39458cf17019132e201c901fb0001f65137c705f2e191fa4021f001fa40d20031fa000c820afaf080a121945315a0a1de22d70b01c300209206a19136e220c2fff2e192218e3dc8500acf16500ccf16821005138d9171245146104f50f2708010c8cb055007cf165005fa0215cb6a12cb1fcb3f226eb39458cf17019132e201c901fb0094102c395be20209007e8e3428f00148508210d53276db016d71708010c8cb055007cf165005fa0215cb6a12cb1fcb3f226eb39458cf17019132e201c901fb0093303436e25504f00301a48e3e3035365b347082108b77173504c8cbff58cf164430128040708010c8cb055007cf165005fa0215cb6a12cb1fcb3f226eb39458cf17019132e201c901fb00e0350582104eb1f0f9bae3025f08840ff2f00b007a5153c705f2e19101d3ff20d74ac20008d0d30701c000f2e19cf404300898d43040178307f417983050068307f45b30e270c8cb07f400c910355512f00300113e910c30003cb853600201200e0f00433b513434fffe900835d27080271fc07e903535350c04118411780c1c165b5b5b5b600023017232ffd40133c59633c5b33333327b55200201201112004bbc265f801282b2f82b8298064459ba37b74678b658382680a678b09e58380e8678b6583e4e840201201314000db8fcff0023031802012015160011b64a5e0042cbe0da1000c7b461843ae9240f152118001e5c08de004204cbe0da1a60e038001e5c339e8086007ae140f8001e5c33b84111c466105e033e04883dcb11fb64ddc4964ad1ba06b879240dc23572f37cc5caaab143a2fffbc4180012660f003c003060fe81edf4260f0030e2c98244",
    # *.with.gram
    "56564209818845235193731369805153860358785566902185149813454663071573327009400": "b5ee9c7241021b010003d5000114ff00f4a413f4bcf2c80b0102016202140202cd0311020120040e020120050d04b10c8871c02497c0f83434c0c05c6c2497c0f83e90087c007e900c7e800c5c75c87e800c7e800c1cea6d0000b4c7f4cffc01016cf8c089f00078c089e08417f30f452ea3a24dd205915d44c536cf380e4e4960840bf2c9a8aea00608090b01f25b323435355233c705f2e1916d70c8cb07f400c904fa40d420c701c0008e42fa00218e3a821005138d9170c829cf165003cf162504503373708010c8cb055007cf165005fa0215cb6a12cb1fcb3f226eb39458cf17019132e201c901fb00915be29130e2820afaf08070fb027082107b4b42e62603066d8306070054708010c8cb055007cf165005fa0215cb6a12cb1fcb3f226eb39458cf17019132e201c901fb005042f005009210245f0435355b21c705f2e191708210e8a0abfe21c805fa403015cf16103441308040708010c8cb055007cf165005fa0215cb6a12cb1fcb3f226eb39458cf17019132e201c901fb0001f65136c705f2e191fa4021f001fa40d20031fa000b820afaf080a121945315a0a1de22d70b01c300209206a19136e220c2fff2e192218e3dc85009cf16500bcf16821005138d9171245146104e50e2708010c8cb055007cf165005fa0215cb6a12cb1fcb3f226eb39458cf17019132e201c901fb0094102b385be2020a007e8e3427f00147408210d53276db016d71708010c8cb055007cf165005fa0215cb6a12cb1fcb3f226eb39458cf17019132e201c901fb0093303335e25503f00501a28e3d35365b347082108b77173504c8cbff58cf164430128040708010c8cb055007cf165005fa0215cb6a12cb1fcb3f226eb39458cf17019132e201c901fb00e0340482104eb1f0f9bae3025f07840ff2f00c00745146c705f2e191d3ff20d74ac20006d0d30701c000f2e19cf404300698d43040158307f417983050048307f45b30e270c8cb07f400c94404f00500113e910c30003cb853600201200f100019343500740075007400750c342000331c14c0321401b3c58572c1d400f3c584f2c1d633c5b2c1f274200201481213003f3b513434fffe900835d2708026dfc07e9035350c040d440d380c1c165b5b5b600021013232ffd400f3c58073c5b333327b552002012015160015bc265f8023628f8017801c0201201718001bb8fcff00431f00231c832cf16c98020120191a0015b64a5e008d8a3e004d843000c5b461843ae9240f152118001e5c08de0082abe0ba1a60e038001e5c339e8086007ae140f8001e5c33b84111c466105e033e04883dcb11fb64ddc4964ad1ba06b879240dc23572f37cc5caaab143a2fffbc4180012660f003c003060fe81edf4260f0030fd909af9",
}


def slice_hash(s: str) -> str:
    cell = begin_cell().store_snake_string(s).end_cell()
    return cell.hash.hex()


def calculate_nft_address_hash(subdomain: str, collection_addr_hash: str) -> str:
    collection_address = Address((0, int(collection_addr_hash).to_bytes(32, byteorder="big")))
    index = int.from_bytes(bytes.fromhex(slice_hash(subdomain)), "big", signed=False)

    data = begin_cell().store_uint(index, 256).store_address(collection_address).end_cell()
    item_code = ITEM_CODES.get(collection_addr_hash, ITEM_CODES.get("base"))
    code = Cell.one_from_boc(item_code)

    state_init = StateInit(code=code, data=data)
    return state_init.serialize().hash.hex()


def create_item_metadata(collection_addr_hash: str, subdomain: str, domain: str, tld: str) -> Dict[str, str]:
    if tld not in SUPPORTED_TLD:
        raise HTTPException(status_code=400, detail="Unsupported TLD")
    if tld == "gram":
        description = f"A .{domain}.{tld} blockchain domain. Gram DNS is a service that allows users to assign a human-readable name to crypto wallets, smart contracts, and websites."
    else:
        description = f"A .{domain}.{tld} blockchain domain. TON DNS allows assigning human-readable names to wallets, smart contracts, and websites."
    return {
        "attributes": [
            {
                "trait_type": "length",
                "value": str(len(subdomain)),
            }
        ],
        "buttons": [
            {
                "label": "⚙️ Manage",
                "uri": f"https://t.me/tondnsx_bot?startapp=manage__address__0--3A{calculate_nft_address_hash(subdomain, collection_addr_hash)}",
            }
        ],
        "description": description
    }
