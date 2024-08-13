import { useState } from "react"

interface IMethodCallInterface {
    methodFunction: () => Promise<void>,
    text: string
}

const MethodCall = ({methodFunction, text}: IMethodCallInterface) => {
    const [loading, setLoading] = useState<boolean>(false)

    const callMethodFunction = async () => {
        setLoading(true);
        await methodFunction();
        setLoading(false);
    }

    return (
        <button className="btn m-2" onClick={callMethodFunction}>
            {loading ? <span className = "loading loading-spinner"/> : text}
        </button>
    );
}

export default MethodCall
