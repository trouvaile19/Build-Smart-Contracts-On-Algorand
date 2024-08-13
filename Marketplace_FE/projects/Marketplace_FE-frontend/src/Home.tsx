// src/components/Home.tsx
import * as algokit from '@algorandfoundation/algokit-utils'
import { useWallet } from '@txnlab/use-wallet'
import React, { useEffect, useState } from 'react'
import AppCalls from './components/AppCalls'
import ConnectWallet from './components/ConnectWallet'
import MethodCall from './components/methodCall'
import Transact from './components/Transact'
import { MarketplaceClient } from './contracts/Marketplace'
import * as methods from './methods'
import { getAlgodConfigFromViteEnvironment } from './utils/network/getAlgoClientConfigs'
interface HomeProps {}

const Home: React.FC<HomeProps> = () => {
  algokit.Config.configure({populateAppCallResources: true})

  const [openWalletModal, setOpenWalletModal] = useState<boolean>(false)
  const [openDemoModal, setOpenDemoModal] = useState<boolean>(false)
  const [appCallsDemoModal, setAppCallsDemoModal] = useState<boolean>(false)
  const { activeAddress, signer } = useWallet()
  const [appId, setAppId] = useState<number>(0)
  const [unitaryPrice, setUnitaryprice] = useState<bigint>(0n)
  const [assetID, setAssetId] = useState<bigint>(0n)
  const [quantity, setquantity] = useState<bigint>(0n)
  const [seller, setSeller] = useState<string>("")
  const [unitsLeft, setUnitleft] = useState<bigint>(0n)


  const toggleWalletModal = () => {
    setOpenWalletModal(!openWalletModal)
  }
  const algodConfig = getAlgodConfigFromViteEnvironment();
  const algorand = algokit.AlgorandClient.fromConfig({algodConfig});
  algorand.setDefaultSigner(signer);

  const dmClient = new MarketplaceClient({
    resolveBy: 'id',
    id: appId,
    sender: {addr: activeAddress!, signer}
  }, algorand.client.algod)

  return (
    <div className="hero min-h-screen bg-teal-400">
      <div className="hero-content text-center rounded-lg p-6 max-w-md bg-white mx-auto">
        <div className="max-w-md">
          <h1 className="text-4xl">
            Welcome to <div className="font-bold">AlgoKit 🙂</div>
          </h1>
          <p className="py-6">
            This starter has been generated using official AlgoKit React template. Refer to the resource below for next steps.
          </p>

          <div className="grid">
            <a
              data-test-id="getting-started"
              className="btn btn-primary m-2"
              target="_blank"
              href="https://github.com/algorandfoundation/algokit-cli"
            >
              Getting started
            </a>

            <div className="divider" />
            <button data-test-id="connect-wallet" className="btn m-2" onClick={toggleWalletModal}>
              Wallet Connection
            </button>
            <label className = "label">Unitary Price</label>
            <input
              type = "number"
              value ={appId}
              min = {0}
              className='input input-bordered'
              onChange = {(e) => {
                setAppId(e.currentTarget.valueAsNumber)
              } }
            />

            {
              activeAddress && appId === 0 && (
                <div>
                  <label className = "label">Unitary Price</label>
                  <input
                    type = "number"
                    value ={(unitaryPrice / BigInt(1e6)).toString()}
                    className='input input-bordered'
                    onChange = {(e) => {
                      setUnitaryprice(BigInt(e.currentTarget.valueAsNumber || 0) * BigInt(1e6) )
                    } }
                  />
                  <label className = "label">Unitary Price</label>
                  <input
                    type = "number"
                    value ={quantity.toString()}
                    className='input input-bordered'
                    onChange = {(e) => {
                      setquantity(BigInt(e.currentTarget.valueAsNumber))
                    } }
                  />
                  <MethodCall
                    methodFunction={methods.create(algorand, dmClient, activeAddress!, unitaryPrice, quantity, assetID, setAppId)}
                    text = " Create Application"
                  />
                </div>
              )
            }


          </div>

          <ConnectWallet openModal={openWalletModal} closeModal={toggleWalletModal} />
          <Transact openModal={openDemoModal} setModalState={setOpenDemoModal} />
          <AppCalls openModal={appCallsDemoModal} setModalState={setAppCallsDemoModal} />
        </div>
      </div>
    </div>
  )
}

export default Home
