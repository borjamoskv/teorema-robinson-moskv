'use client';

import { motion } from 'framer-motion';

export default function PatientBookingPortal() {
  return (
    <div className="min-h-screen bg-black text-white flex flex-col items-center justify-center p-4">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        className="max-w-md w-full"
      >
        <div className="text-center mb-10">
          <h1 className="text-3xl font-black uppercase tracking-tight text-white mb-2">Book an Appointment</h1>
          <p className="text-muted-foreground text-sm font-mono">Select a service below</p>
        </div>

        <div className="space-y-4">
          {[
            { id: 1, name: 'Initial Consultation', duration: '45 min', price: '$150' },
            { id: 2, name: 'Follow-up Session', duration: '30 min', price: '$90' },
            { id: 3, name: 'Advanced Diagnostics', duration: '60 min', price: '$250' },
          ].map((service, i) => (
            <motion.button
              key={service.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 + i * 0.1 }}
              className="w-full text-left bg-[#111111] hover:bg-[#1a1a1a] border border-border hover:border-primary transition-all p-6 flex justify-between items-center group"
            >
              <div>
                <h3 className="text-lg font-bold text-white group-hover:text-primary transition-colors">{service.name}</h3>
                <p className="text-sm font-mono text-muted-foreground mt-1">{service.duration}</p>
              </div>
              <div className="text-lg font-black text-white">
                {service.price}
              </div>
            </motion.button>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
