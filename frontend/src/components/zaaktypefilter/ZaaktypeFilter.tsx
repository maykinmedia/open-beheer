import {
  Body,
  Card,
  Dropdown,
  Form,
  FormControlProps,
  Input,
  Option,
  P,
  SerializedFormData,
  Solid,
  ToolbarItem,
} from "@maykin-ui/admin-ui";
import { FormEvent, useCallback, useState } from "react";
import { useDebounce } from "~/hooks/useDebounce.tsx";

import "./zaaktypeFilter.css";

export type ZaaktypeFilterValues = {
  /** The value for "status". */
  status?: ZaaktypeStatusEnum | null;

  /** The value for "trefwoorden". */
  trefwoorden?: string | null;
};

export type ZaaktypeFilterProps = ZaaktypeFilterValues & {
  /** Gets called if the form is submitted. */
  onSubmit?: (data: ZaaktypeFilterValues & { page: 1 }) => void;
};

const StatusChoices = [
  {
    label: "Alles",
    value: "alles",
  },
  {
    label: "Concept",
    value: "concept",
  },
  {
    label: "Definitief",
    value: "definitief",
  },
] as const satisfies Option[];
export type ZaaktypeStatusEnum = (typeof StatusChoices)[number]["value"];

/**
 * Zaaktype filter component
 */
export function ZaaktypeFilter({
  status,
  trefwoorden,
  onSubmit,
}: ZaaktypeFilterProps) {
  const [isDropDownOpen, setIsDropDownOpen] = useState(false);
  const [statusState, setStatusState] = useState<ZaaktypeStatusEnum | null>(
    status || null,
  );
  const [trefwoordenState, setTrefwoordenState] = useState(trefwoorden);

  /**
   * Calls onSubmit with the entered value.
   */
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTrefwoordenState(e.target.value);
    handleSubmit(e, { trefwoorden: e.target.value });
  };

  /**
   * Toggles the dropdown open state.
   */
  const handleToggle = useCallback(() => {
    setIsDropDownOpen(!isDropDownOpen);
  }, [isDropDownOpen]);

  /**
   * Calls onSubmit with empty values.
   */
  const handleReset = useCallback(() => {
    setStatusState(null);
    setTrefwoordenState(null);
    onSubmit?.({ status: null, trefwoorden: null, page: 1 });
  }, [onSubmit]);

  /**
   * Maps the onSubmit of the Form to onSubmit.
   */
  const handleSubmit = useCallback(
    useDebounce((_: FormEvent, data: SerializedFormData = {}) => {
      const values = data as ZaaktypeFilterValues;
      onSubmit?.({
        status: values.status || statusState,
        trefwoorden: values.trefwoorden,
        page: 1, // Filtering invalidates pagination.
      });
    }, 500), // MacOS delay until repeat
    [trefwoordenState, onSubmit],
  );

  const fields: FormControlProps[] = [
    {
      label: "Status",
      name: "status",
      type: "radio",
      value: statusState,
      options: StatusChoices,
      // TODO: Type should be HTMLInputElement as this is a radio.,
      onChange: (e: React.ChangeEvent<HTMLSelectElement>) =>
        setStatusState(e.target.value as ZaaktypeStatusEnum),
    },
  ];

  const secondaryActions: ToolbarItem[] = [
    {
      children: "Wis alle filters",
      pad: "h",
      variant: "danger",
      type: "reset",
    },
    "spacer",
    {
      children: "Annuleer",
      pad: "h",
      variant: "secondary",
      onClick: handleToggle,
    },
  ];
  return (
    <div className="ob-zaaktype-filter">
      <Input
        aria-label="Trefwoorden"
        icon={<Solid.MagnifyingGlassIcon />}
        name="trefwoorden"
        placeholder="Trefwoorden"
        value={trefwoordenState || ""}
        onChange={handleSearch}
      />
      <Dropdown
        className="ob-zaaktype-filter__filter"
        open={isDropDownOpen}
        variant="outline"
        label={
          <>
            <Solid.AdjustmentsHorizontalIcon />
            Filter
          </>
        }
        toolbar={false}
        onClick={handleToggle}
        onClose={handleToggle}
      >
        <Card>
          <Body>
            <P bold>Filters</P>
            <Form
              buttonProps={{ pad: "h" }}
              fields={fields}
              labelSubmit="Pas toe"
              secondaryActions={secondaryActions}
              showRequiredExplanation={false}
              onReset={handleReset}
              onSubmit={handleSubmit}
            />
          </Body>
        </Card>
      </Dropdown>
    </div>
  );
}
