import { useState } from "react";
interface ImethodCallInterface {
    methodFunction: () => Promise<void>,
    text: string
}

const MethodCall = ({methodFunction, text}: ImethodCallInterface ) => {
    const [loading, setLoading] = useState<boolean>(false);

    const callMethodFunction = async () => {
        setLoading(true);
        await methodFunction;
        setLoading(false);
    }
    return(
        <button className = "btn m-2" onClick = {callMethodFunction}>
            {loading ? <span className = "loading loading-spinner"/> : text}
        </button>
    )
}
export default MethodCall
