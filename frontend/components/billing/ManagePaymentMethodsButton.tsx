"use client";

import { useState } from "react";
import CardIcon from "@/components/svg/CardIcon";
import Button from "@/components/ui/Button";
import { createPortalSession } from "@/lib/api/billing";

/**
 * Sends the fan to the Stripe Customer Portal to manage their payment methods
 * (and cancel / view invoices). Opening the portal is a backend round-trip for a
 * one-time URL, so we show a pending state and redirect the whole page on
 * success. Only render this for fans who have a subscription — the endpoint 400s
 * for anyone without a Stripe Customer yet.
 */
export default function ManagePaymentMethodsButton() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  async function openPortal() {
    setError(false);
    setLoading(true);
    try {
      const { portal_url } = await createPortalSession();
      window.location.href = portal_url;
    } catch {
      // Redirect failed before navigating away — let the fan retry.
      setError(true);
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col items-start gap-1 sm:items-end">
      <Button
        variant="outline"
        onClick={openPortal}
        disabled={loading}
        className="gap-2"
      >
        <CardIcon className="h-4 w-4" />
        {loading ? "Opening…" : "Manage payment methods"}
      </Button>
      {error && (
        <p className="text-sm text-red-600 dark:text-red-400">
          Couldn&apos;t open billing — please try again.
        </p>
      )}
    </div>
  );
}
