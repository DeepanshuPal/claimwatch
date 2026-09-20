import type { Metadata } from "next";
import Link from "next/link";
import "./style.css";

export const metadata: Metadata = {metadataBase:new URL("https://deepanshupal.github.io/watch-my-handle"),title:{default:"Watch My Handle - Know when a name moves",template:"%s - Watch My Handle"},description:"Watch My Handle watches handles and domains and alerts you when availability, ownership, or activity changes.",openGraph:{title:"Watch My Handle",description:"Watch handles and domains. Know when a name moves.",url:"https://deepanshupal.github.io/watch-my-handle",siteName:"Watch My Handle",type:"website"}};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body><header className="nav"><Link className="brand" href="/">Watch My Handle<span>.</span></Link><nav><Link href="/check">Check a name</Link><Link href="/pricing">Pricing</Link><Link href="/docs">Docs</Link><a href="https://github.com/DeepanshuPal/watch-my-handle">GitHub</a></nav></header>{children}<footer><span>Watch My Handle is open source.</span><a href="https://github.com/DeepanshuPal/watch-my-handle">MIT on GitHub ↗</a></footer></body></html>}
