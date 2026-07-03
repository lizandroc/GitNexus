import { NextResponse } from "next/server";

/**
 * Contact form endpoint — MVP implementation.
 *
 * Validates the submission and logs it server-side. Wire it to your real
 * destination by replacing the `deliver` function: send an email (Resend,
 * SES, Postmark), post to a CRM webhook, or append to a database.
 */

type ContactPayload = {
  name?: string;
  company?: string;
  email?: string;
  phone?: string;
  industry?: string;
  timeline?: string;
  goals?: string;
  deployment?: string;
};

async function deliver(payload: Required<Pick<ContactPayload, "name" | "company" | "email" | "goals">> & ContactPayload) {
  // MVP: log to the server console. Replace with email/CRM delivery.
  console.log("[contact] new inquiry:", JSON.stringify(payload, null, 2));
}

export async function POST(request: Request) {
  let body: ContactPayload;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid request body." }, { status: 400 });
  }

  const name = (body.name || "").trim();
  const company = (body.company || "").trim();
  const email = (body.email || "").trim();
  const goals = (body.goals || "").trim();

  if (!name || !company || !email || !goals) {
    return NextResponse.json(
      { error: "Please fill in name, company, email, and what you want AI to help with." },
      { status: 400 }
    );
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return NextResponse.json({ error: "Please enter a valid email address." }, { status: 400 });
  }
  if (goals.length > 5000 || name.length > 200 || company.length > 200) {
    return NextResponse.json({ error: "One of the fields is too long." }, { status: 400 });
  }

  await deliver({ ...body, name, company, email, goals });
  return NextResponse.json({ ok: true });
}
