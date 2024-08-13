import * as algokit from '@algorandfoundation/algokit-utils';
import { MarketplaceClient } from './contracts/Marketplace';

export function create(
    algogrand: algokit.AlgorandClient,
    dmClient: MarketplaceClient,
    sender: string,
    unitaryPrice: bigint,
    quantity: bigint,
    assetBeingSold: bigint,
    setAppId: (id: number) => void,
) {
    return async () => {
        let assetId = assetBeingSold;

        if (assetId === 0n) {
            const assetCreate = await algogrand.send.assetCreate({
                sender,
                total: quantity
            }); // create tokens

            assetId = BigInt(assetCreate.confirmation.assetIndex!)
        }

        const createResult = await dmClient.create.createApplication({assetId, unitaryPrice})

        const Txn = await algogrand.transactions.payment({
            sender,
            receiver: createResult.appAddress,
            amount: algokit.algos(0.2),
            extraFee: algokit.algos(0.001) // function → Algorand → 0.001algos
        });

        await dmClient.optInToAsset({pay: Txn});

        await algogrand.send.assetTransfer({
            assetId,
            sender,
            receiver: createResult.appAddress,
            amount: quantity
        });

        setAppId(Number(createResult.appId));
    }
}
