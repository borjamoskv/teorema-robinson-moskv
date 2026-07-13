import { headers } from 'next/headers';
import { NextResponse } from 'next/server';
import Stripe from 'stripe';
import { stripe } from '@/lib/stripe';
import { db } from '@/db';
import { agencies, tenants, appointments, subscriptions, invoices } from '@/db/schema';
import { eq } from 'drizzle-orm';
import crypto from 'crypto';

export async function POST(req: Request) {
  const body = await req.text();
  const signature = (await headers()).get('Stripe-Signature') as string;

  let event: Stripe.Event;

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

  try {
    switch (event.type) {
      case 'account.updated': {
        const account = event.data.object as Stripe.Account;
        // Logic to update agency or clinic onboarding status in DB
        break;
      }
      
      case 'checkout.session.completed': {
        const session = event.data.object as Stripe.Checkout.Session;
        if (session.metadata?.appointmentId) {
          await db.update(appointments)
            .set({ status: 'confirmed' })
            .where(eq(appointments.id, session.metadata.appointmentId));
        }
        break;
      }

      case 'customer.subscription.created':
      case 'customer.subscription.updated': {
        const subscription = event.data.object as Stripe.Subscription;
        const customerId = subscription.customer as string;
        let agencyId = subscription.metadata?.agencyId;

        if (!agencyId) {
          const existingSub = await db.query.subscriptions.findFirst({
            where: eq(subscriptions.stripeCustomerId, customerId),
          });
          if (existingSub) {
            agencyId = existingSub.agencyId;
          } else {
            const customer = await stripe.customers.retrieve(customerId);
            if (!customer.deleted && customer.metadata?.agencyId) {
              agencyId = customer.metadata.agencyId;
            }
          }
        }

        if (agencyId) {
          const subData = {
            agencyId,
            stripeCustomerId: customerId,
            stripeSubscriptionId: subscription.id,
            stripePriceId: subscription.items.data[0].price.id,
            status: subscription.status,
            currentPeriodStart: new Date(subscription.current_period_start * 1000),
            currentPeriodEnd: new Date(subscription.current_period_end * 1000),
            cancelAtPeriodEnd: subscription.cancel_at_period_end,
            updatedAt: new Date(),
          };

          await db.insert(subscriptions)
            .values({ ...subData, id: crypto.randomUUID() })
            .onConflictDoUpdate({
              target: subscriptions.stripeSubscriptionId,
              set: subData,
            });
        }
        break;
      }

      case 'customer.subscription.deleted': {
        const subscription = event.data.object as Stripe.Subscription;
        await db.update(subscriptions)
          .set({
            status: 'canceled',
            updatedAt: new Date(),
          })
          .where(eq(subscriptions.stripeSubscriptionId, subscription.id));
        break;
      }

      case 'invoice.payment_succeeded': {
        const invoiceObj = event.data.object as Stripe.Invoice;
        if (invoiceObj.subscription) {
          let agencyId;
          const existingSub = await db.query.subscriptions.findFirst({
            where: eq(subscriptions.stripeSubscriptionId, invoiceObj.subscription as string),
          });
          if (existingSub) {
            agencyId = existingSub.agencyId;
          }

          if (agencyId) {
            const invoiceData = {
              agencyId,
              stripeInvoiceId: invoiceObj.id,
              amountCents: invoiceObj.amount_paid,
              currency: invoiceObj.currency,
              status: invoiceObj.status || 'paid',
              hostedInvoiceUrl: invoiceObj.hosted_invoice_url,
              updatedAt: new Date(),
            };

            await db.insert(invoices)
              .values({ ...invoiceData, id: crypto.randomUUID() })
              .onConflictDoUpdate({
                target: invoices.stripeInvoiceId,
                set: invoiceData,
              });
          }
        }
        break;
      }

      default:
        break;
    }
  } catch (error) {
    const e = error as Error;
    return NextResponse.json({ error: `Webhook handler failed: ${e.message}` }, { status: 500 });
  }

  return NextResponse.json({ received: true });
}

