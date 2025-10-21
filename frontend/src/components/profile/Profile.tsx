import {
  Body,
  Button,
  Card,
  Column,
  Dropdown,
  Grid,
  H3,
  Hr,
  IconInitials,
  P,
  Solid,
} from "@maykin-ui/admin-ui";
import React from "react";
import { NavLink } from "react-router";
import { formatUser } from "~/lib";
import { components } from "~/types";

type ProfileProps = {
  user: components["schemas"]["User"] | null;
};

export const Profile: React.FC<ProfileProps> = ({ user }) => {
  if (!user) {
    return null;
  }

  const name = user ? formatUser(user, { showUsername: false }) : "";

  return (
    <Dropdown
      aria-label="Profiel"
      key="account"
      label={<IconInitials name={name} />}
      pad="v"
      variant="transparent"
    >
      <Body>
        <Card>
          <H3>Account</H3>
          <Hr />
          <Grid>
            <Column containerType="normal" span={2}>
              <IconInitials name={name} />
            </Column>
            <Column span={8}>
              <Grid gutter={false}>
                <Column span={12}>
                  <P bold>
                    {user?.firstName} {user?.lastName}
                  </P>
                </Column>
                <Column span={12}>
                  <P muted>{user?.email}</P>
                </Column>
              </Grid>
            </Column>
            <Hr />
            <Column span={6} />
            <Column span={6}>
              <NavLink key="logout" to="logout">
                <Button variant="outline" aria-label="Logout">
                  <Solid.ArrowRightEndOnRectangleIcon /> Uitloggen
                </Button>
              </NavLink>
            </Column>
          </Grid>
        </Card>
      </Body>
    </Dropdown>
  );
};
