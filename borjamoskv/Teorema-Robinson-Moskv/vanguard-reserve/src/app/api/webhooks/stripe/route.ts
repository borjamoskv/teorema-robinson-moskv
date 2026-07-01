import { headers } from 'next/headers';
import { NextResponse } from 'next/server';
import { stripe } from '@/lib/stripe';
import { db } from '@/db';
import { agencies, tenants, appointments } from '@/db/schema';
import { eq } from 'drizzle-orm';

export async function POST(req: Request) {
  const body = await req.text();
  const signature = (await headers()).get('Stripe-Signature') as string;

  let event;

  try {
    event = stripe.webhooks.constructEvent(
      body,
      signature,
      process.env.STRIPE_WEBHOOK_SECRET || 'whsec_mock'
    );
  } catch (error) {
    const e = error as Error;
    return NextResponse.json({ error: e.message }, { status: 400 });
  }

  // Handle B2B2B Events (Stripe Connect & Subscriptions)
  try {
    switch (event.type) {
      case 'account.updated': {
        const account = event.data.object as Stripe.Account;
        // Logic to update agency or clinic onboarding status in DB
        break;
      }
      case 'checkout.session.completed': {
        const session = event.data.object as Stripe.Checkout.Session;
        // Logic to confirm appointment and distribute funds
        if (session.metadata?.appointmentId) {
          await db.update(appointments)
            .set({ status: 'confirmed' })
            .where(eq(appointments.id, session.metadata.appointmentId));
        }
        break;
      }
      // Add other B2B2B events: payment_intent.succeeded, customer.subscription.created, etc.
      default:
        break;
    }
  } catch (error) {
    return NextResponse.json({ error: 'Webhook handler failed' }, { status: 500 });
  }

  return NextResponse.json({ received: true });
}
