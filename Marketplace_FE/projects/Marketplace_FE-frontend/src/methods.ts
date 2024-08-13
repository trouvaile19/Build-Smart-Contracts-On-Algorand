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

        await dmClient.optInToAsset({pay: Txn})

        await algogrand.send.assetTransfer({
            assetId,
            sender,
            receiver: createResult.appAddress,
            amount: quantity
        });

        setAppId(Number(createResult.appId));
    }
}
export function buy(
  algogrand: algokit.AlgorandClient,
  dmClient: MarketplaceClient,
  sender: string,
  appAddress: string,
  quantity: bigint,
  unitaryPrice: bigint,
  setUnitsLeft: React.Dispatch<React.SetStateAction<bigint>>
) {
  return async () => {
      const buyerTxn = await algogrand.transactions.payment({
          sender,
          receiver: appAddress,
          amount: algokit.microAlgos(Number(quantity * unitaryPrice)),
          extraFee: algokit.algos(0.001)
      })

      await dmClient.buy({
          payer: buyerTxn,
          quantity
      })

      const state = await dmClient.getGlobalState();
      const info = await algogrand.account.getAssetInformation(appAddress, state.assetId!.asBigInt())
      setUnitsLeft(info.balance)
  }
}

export function deleteApp(
  dmClient: MarketplaceClient,
  setAppId: (id: number) => void
) {
  return async () => {
      await dmClient.delete.deleteApplication({}, {sendParams: {fee: algokit.algos(0.003)}})
      setAppId(0)
  }
}
