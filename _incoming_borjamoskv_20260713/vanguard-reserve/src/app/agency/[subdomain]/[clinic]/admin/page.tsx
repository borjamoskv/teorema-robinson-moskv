export default async function ClinicAdminDashboard({
  params,
}: {
  params: Promise<{ subdomain: string, clinic: string }>;
}) {
  const { subdomain, clinic } = await params;

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <header className="mb-12 border-b border-border pb-6 flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-black tracking-tight text-white uppercase">{clinic}</h1>
          <p className="text-muted-foreground mt-2 font-mono text-sm">AGENCY: {subdomain} | CLINIC DASHBOARD</p>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
        <div className="border border-border bg-[#0d0d0d] p-6 hover:border-primary transition-colors">
          <h2 className="text-lg font-bold text-muted-foreground mb-2 uppercase text-xs tracking-widest">Appointments Today</h2>
          <div className="text-4xl font-black text-primary">24</div>
        </div>
        <div className="border border-border bg-[#0d0d0d] p-6 hover:border-primary transition-colors">
          <h2 className="text-lg font-bold text-muted-foreground mb-2 uppercase text-xs tracking-widest">Revenue Today</h2>
          <div className="text-4xl font-black text-white">$2,150</div>
        </div>
      </div>
      
      <div className="border border-border bg-[#0d0d0d] p-8">
        <h2 className="text-xl font-bold text-white mb-6 uppercase">Schedule</h2>
        <div className="text-center py-12 text-muted-foreground font-mono">
          Calendar Module Loading...
        </div>
      </div>
    </div>
  );
}
