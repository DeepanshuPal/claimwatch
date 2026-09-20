import type { Metadata } from "next";
import Link from "next/link";
import "./style.css";

export const metadata: Metadata = {metadataBase:new URL("https://claimwatch.vercel.app"),title:{default:"Claimwatch - Know when a name moves",template:"%s - Claimwatch"},description:"Watch handles and domains. Get pinged when availability, ownership, or activity changes.",openGraph:{title:"Claimwatch",description:"Know when a name moves.",type:"website"}};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body><header className="nav"><Link className="brand" href="/">Claimwatch<span>.</span></Link><nav><Link href="/check">Check a name</Link><Link href="/pricing">Pricing</Link><Link href="/docs">Docs</Link><a href="https://github.com/DeepanshuPal/claimwatch">GitHub</a></nav></header>{children}<footer><span>Claimwatch is open source.</span><a href="https://github.com/DeepanshuPal/claimwatch">MIT on GitHub ↗</a></footer></body></html>}
