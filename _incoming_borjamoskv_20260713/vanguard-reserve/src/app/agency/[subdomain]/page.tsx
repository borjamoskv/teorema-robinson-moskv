export default async function AgencyDashboard({
  params,
}: {
  params: Promise<{ subdomain: string }>;
}) {
  const { subdomain } = await params;

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <header className="mb-12 border-b border-border pb-6">
        <h1 className="text-4xl font-black tracking-tight text-white uppercase">AGENCY KERNEL: {subdomain}</h1>
        <p className="text-muted-foreground mt-2 font-mono text-sm">VANGUARD-RESERVE MULTI-TENANT ENGINE</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="border border-border bg-[#0d0d0d] p-6 hover:border-primary transition-colors">
          <h2 className="text-lg font-bold text-muted-foreground mb-2 uppercase text-xs tracking-widest">Active Clinics</h2>
          <div className="text-4xl font-black text-primary">12</div>
        </div>
        <div className="border border-border bg-[#0d0d0d] p-6 hover:border-primary transition-colors">
          <h2 className="text-lg font-bold text-muted-foreground mb-2 uppercase text-xs tracking-widest">Monthly Revenue</h2>
          <div className="text-4xl font-black text-white">$4,250</div>
        </div>
        <div className="border border-border bg-[#0d0d0d] p-6 hover:border-primary transition-colors">
          <h2 className="text-lg font-bold text-muted-foreground mb-2 uppercase text-xs tracking-widest">System Status</h2>
          <div className="text-xl font-bold text-green-500 mt-2 flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></span>
            OPERATIONAL
          </div>
        </div>
      </div>
    </div>
  );
}
