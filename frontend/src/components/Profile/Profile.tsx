import {
  Body,
  ButtonLink,
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
import React, { useEffect, useState } from "react";
import { User, whoAmI } from "~/api/auth.ts";
import { formatUser } from "~/format/formatUser.ts";

type ProfileProps = object;

export const Profile: React.FC<ProfileProps> = () => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const currentUser = await whoAmI();
        setUser(currentUser);
      } catch (error) {
        console.error("Failed to fetch user:", error);
      }
    };

    void fetchUser();
  }, []);

  return (
    <Dropdown
      aria-label="Profiel"
      key="account"
      label={
        <IconInitials
          name={user ? formatUser(user as User, { showUsername: false }) : ""}
        />
      }
      pad="v"
      variant="transparent"
    >
      <Body>
        <Card>
          <H3>Account</H3>
          <Hr />
          <Grid>
            <Column containerType="normal" span={2}>
              <IconInitials
                name={
                  user
                    ? formatUser(user as User, {
                        showUsername: false,
                      })
                    : ""
                }
              />
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
              <ButtonLink href={"/logout"} variant="outline" wrap={false}>
                <Solid.ArrowRightEndOnRectangleIcon />
                Uitloggen
              </ButtonLink>
            </Column>
          </Grid>
        </Card>
      </Body>
    </Dropdown>
  );
};
